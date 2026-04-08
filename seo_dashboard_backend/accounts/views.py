from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def google_auth(request):
    credential = request.data.get("credential")

    if not credential:
        return Response({"error": "credential manquant"}, status=400)

    if not settings.GOOGLE_WEB_CLIENT_ID:
        return Response(
            {"error": "Configuration Google Login manquante sur le serveur"},
            status=500,
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_WEB_CLIENT_ID,
        )
    except Exception as e:
        return Response(
            {"error": f"Token Google invalide: {str(e)}"},
            status=400,
        )

    email = idinfo.get("email")
    given_name = idinfo.get("given_name", "")

    if not email:
        return Response({"error": "Email Google introuvable"}, status=400)

    username_base = email.split("@")[0]
    username = username_base

    user = User.objects.filter(email=email).first()

    if not user:
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=given_name,
            password=None,
        )
        user.set_unusable_password()
        user.save()

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
            },
        },
        status=200,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get("email")

    if not email:
        return Response({"error": "Email requis"}, status=400)

    user = User.objects.filter(email=email).first()

    if not user:
        return Response(
            {"message": "Si cet email existe, un lien a ete genere."},
            status=200,
        )

    if not user.has_usable_password():
        return Response(
            {"error": "Ce compte utilise Google. Connectez-vous avec Google."},
            status=400,
        )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

    send_mail(
        subject="Reinitialisation du mot de passe",
        message=f"Cliquez sur ce lien pour reinitialiser votre mot de passe : {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response(
        {"message": "Email de reinitialisation envoye avec succes."},
        status=200,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    uidb64 = request.data.get("uid")
    token = request.data.get("token")
    password = request.data.get("password")

    if not uidb64 or not token or not password:
        return Response({"error": "uid, token et password sont requis"}, status=400)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({"error": "Lien invalide"}, status=400)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "Token invalide ou expire"}, status=400)

    user.set_password(password)
    user.save()

    return Response({"message": "Mot de passe reinitialise avec succes"}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_get_users(request):
    """Recuperer tous les utilisateurs (super user uniquement)."""
    if not request.user.is_superuser:
        return Response({"error": "Acces non autorise"}, status=403)

    users = User.objects.all().order_by("-date_joined")
    data = []
    for user in users:
        data.append(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M"),
                "last_login": user.last_login.strftime("%Y-%m-%d %H:%M")
                if user.last_login
                else None,
            }
        )
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_create_user(request):
    """Creer un nouvel utilisateur (super user uniquement)."""
    if not request.user.is_superuser:
        return Response({"error": "Acces non autorise"}, status=403)

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    first_name = request.data.get("first_name", "")
    last_name = request.data.get("last_name", "")
    is_active = request.data.get("is_active", True)

    if not username or not email or not password:
        return Response({"error": "Username, email et password requis"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Ce nom d'utilisateur existe deja"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Cet email existe deja"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )

    try:
        send_mail(
            subject="Bienvenue sur SEOmind",
            message=f"""
Bonjour {username},

Un compte a ete cree pour vous sur la plateforme SEOmind.

Identifiants :
- Nom d'utilisateur : {username}
- Mot de passe : {password}

Connectez-vous ici : {settings.FRONTEND_URL}

Cordialement,
L'equipe SEOmind
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        pass

    return Response(
        {
            "message": f"Utilisateur {username} cree avec succes",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
            },
        },
        status=201,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def admin_update_user(request, user_id):
    """Modifier un utilisateur (activation/desactivation)."""
    if not request.user.is_superuser:
        return Response({"error": "Acces non autorise"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Utilisateur non trouve"}, status=404)

    if user.id == request.user.id and request.user.is_superuser:
        return Response(
            {"error": "Vous ne pouvez pas modifier votre propre compte"},
            status=400,
        )

    is_active = request.data.get("is_active")
    is_superuser = request.data.get("is_superuser")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")

    if is_active is not None:
        user.is_active = is_active
        if is_active:
            try:
                send_mail(
                    subject="Votre compte SEOmind a ete active",
                    message=f"""
Bonjour {user.username},

Votre compte a ete active par l'administrateur.

Connectez-vous ici : {settings.FRONTEND_URL}

Cordialement,
L'equipe SEOmind
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

    if is_superuser is not None:
        user.is_superuser = is_superuser

    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    user.save()

    return Response(
        {
            "message": f"Utilisateur {user.username} modifie avec succes",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            },
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    """Supprimer un utilisateur (super user uniquement)."""
    if not request.user.is_superuser:
        return Response({"error": "Acces non autorise"}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "Utilisateur non trouve"}, status=404)

    if user.id == request.user.id:
        return Response(
            {"error": "Vous ne pouvez pas supprimer votre propre compte"},
            status=400,
        )

    username = user.username
    user.delete()

    return Response({"message": f"Utilisateur {username} supprime avec succes"})
