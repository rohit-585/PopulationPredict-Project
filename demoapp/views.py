


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout,get_user_model
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from demoapp.utils import generate_verification_link
from django.core.mail import send_mail

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from demoapp.utils import send_verification_email

from django.conf import settings 

from plotly.utils import PlotlyJSONEncoder


import plotly.express as px

from .models import MapSelection  # optional DB save
import json


import os
import pickle
import pandas as pd
import plotly.graph_objs as go




@login_required
def home_view(request):
    return render(request, 'home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('predict_form')  # home per jo dikhan hota hia 
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        uname = request.POST['username']
        email = request.POST['email']
        pwd1 = request.POST['password1']
        pwd2 = request.POST['password2']


        User.objects.filter(username=uname, is_active=False).delete()
        User.objects.filter(email=email, is_active=False).delete()

        if User.objects.filter(username=uname).exists():
            messages.error(request, "⚠️ Username already exists.")
            return render(request, 'register.html')

        elif User.objects.filter(email=email).exists():
            messages.error(request, "⚠️ Email already registered.")
            return render(request, 'register.html')

        elif pwd1 != pwd2:
            messages.error(request, "❌ Passwords do not match.")
            return render(request, 'register.html')

        user = User.objects.create_user(username=uname, email=email, password=pwd1)
        user.is_active = False
        user.save()

        send_verification_email(user, request)  # ✅ only one email
        messages.success(request, "📧 Verification email sent. Please check your inbox.")
        return redirect('please_verify')

    return render(request, 'register.html')


def please_verify(request):
    return render(request, 'please_verify.html')

 


def logout_view(request):
    logout(request)
    return redirect('login')



def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "✅ Email verified successfully! Please login.")
        return redirect('login')
    else:
        messages.error(request, "❌ Invalid or expired link.")
        return redirect('register')





def form_view(request):
    # Safer absolute path
    csv_path = os.path.join(settings.BASE_DIR, 'demoapp', 'static', 'final_df_long.csv')
    
    df = pd.read_csv(csv_path)
    states = df["State"].unique().tolist()
    return render(request, 'form.html', {'states': states})



# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))




def data_map_view(request):
    df = pd.read_csv("demoapp/static/india.csv")
    df["Litraci_ration"] = df["Literate"] / df["Population"] * 1000

    states = sorted(df["State"].unique())
    states.insert(0, "Overall India")

    selected_state = request.GET.get("state", "Overall India")
    primary = request.GET.get("primary", "Literate")
    secondary = request.GET.get("secondary", "Population")

    filtered_df = df if selected_state == "Overall India" else df[df["State"] == selected_state]

    fig = px.scatter_mapbox(
        filtered_df,
        lat="Latitude",
        lon="Longitude",
        zoom=4 if selected_state == "Overall India" else 5,
        size=primary,
        color=secondary,
        mapbox_style="carto-positron",
        width=1000,
        height=600,
        hover_name="District"
    )
    graph_html = fig.to_html(full_html=False)

    # Optional: Save selection
    MapSelection.objects.create(
        state=selected_state,
        primary=primary,
        secondary=secondary
    )

    context = {
        'graph': graph_html,
        'states': states,
        'selected_state': selected_state,
        'columns': sorted(df.columns[5:]),
        'primary': primary,
        'secondary': secondary,
    }
    return render(request, 'map.html', context)


# Load all models
FEATURES = ['Population', 'Rural', 'Urban', 'Literacy', 'Sex_Ratio']
MODELS = {}

MODELS_PATH = os.path.join(settings.BASE_DIR, 'models')
for feature in FEATURES:
    with open(os.path.join(MODELS_PATH, f'{feature}_models.pkl'), 'rb') as f:
        MODELS[feature] = pickle.load(f)

def predict_view(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        year = int(request.POST.get('year'))
        growth_type = request.POST.get('growth_type')  # "all", "population", etc.

        result = {
            'State': state,
            'Year': year,
        }

        feature_map = {
            'population': 'Population',
            'rural': 'Rural',
            'urban': 'Urban',
            'literacy': 'Literacy',
            'sex_ratio': 'Sex_Ratio',
            'growth': 'Growth_Rate'
        }

        if growth_type == 'all':
            selected_features = FEATURES
        elif growth_type == 'growth':
            selected_features = ['Population']
        else:
            selected_features = [feature_map.get(growth_type, 'Population')]

        for feature in selected_features:
            model = MODELS.get(feature, {}).get(state)
            if model:
                pred = model.predict([[year]])[0]
                pred = round(pred, 2)
                result[feature] = pred
            else:
                result[feature] = None

        # Handle growth rate
        if 'Population' in selected_features or growth_type == 'growth':
            try:
                pop_this = MODELS['Population'][state].predict([[year]])[0]
                pop_prev = MODELS['Population'][state].predict([[year - 1]])[0]
                growth = ((pop_this - pop_prev) / pop_prev) * 100
                result['Population_Growth_Rate'] = round(growth, 2)
            except:
                result['Population_Growth_Rate'] = None

        # Graph plotting — only for the first selected feature
        selected_for_plot = selected_features[0]
        model = MODELS[selected_for_plot].get(state)
        if model:
            trend_years = list(range(1951, 2012, 10))
            trend_values = [round(model.predict([[y]])[0], 2) for y in trend_years]
            pred_val = round(model.predict([[year]])[0], 2)
            min_val = round(pred_val * 0.95, 2)
            max_val = round(pred_val * 1.05, 2)
        else:
            trend_years = []
            trend_values = []
            pred_val = min_val = max_val = None

        return render(request, 'result.html', {
            'result': result,
            'trend_years_json': json.dumps(trend_years),
            'trend_values_json': json.dumps(trend_values),
            'pred': pred_val,
            'min_val': min_val,
            'max_val': max_val,
            'year': year,
            'feature_name': selected_for_plot
        })

    else:
        csv_path = os.path.join(settings.BASE_DIR, 'demoapp', 'static', 'final_df_long.csv')
        df = pd.read_csv(csv_path)
        states = df["State"].unique().tolist()
        return render(request, 'form.html', {'states': states})

