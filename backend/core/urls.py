from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from django.http import HttpResponse
from apps.auth_app.api import router as auth_router
from apps.programs.api import router as programs_router
from apps.props.api import router as props_router
from apps.vehicles.api import router as vehicles_router
from apps.loading.api import loading_router, unloading_router, damage_router
from apps.dashboard.api import router as dashboard_router

api = NinjaAPI(title='马戏团道具装车与巡演归库系统 API', version='1.0.0')
api.add_router('/auth', auth_router)
api.add_router('/programs', programs_router)
api.add_router('/props', props_router)
api.add_router('/vehicles', vehicles_router)
api.add_router('/loading', loading_router)
api.add_router('/unloading', unloading_router)
api.add_router('/damage', damage_router)
api.add_router('/dashboard', dashboard_router)


def index(request):
    return HttpResponse('<h1>马戏团道具装车与巡演归库系统 API</h1><p>请访问 <a href="/api/docs">/api/docs</a> 查看 API 文档</p>')


urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
