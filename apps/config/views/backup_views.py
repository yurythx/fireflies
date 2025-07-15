from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, HttpResponse, HttpResponseForbidden
from django.conf import settings
import subprocess
import tempfile
import os
import shutil
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect

@staff_member_required
def backup_database(request):
    """Gera um backup do banco PostgreSQL e serve para download"""
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_host = settings.DATABASES['default'].get('HOST', 'localhost')
    db_port = str(settings.DATABASES['default'].get('PORT', '5432'))
    db_password = settings.DATABASES['default'].get('PASSWORD', '')
    with tempfile.NamedTemporaryFile(suffix='.backup', delete=False) as tmpfile:
        tmpfile.close()
        cmd = [
            'pg_dump',
            '-U', db_user,
            '-h', db_host,
            '-p', db_port,
            '-F', 'c',
            '-b',
            '-v',
            '-f', tmpfile.name,
            db_name
        ]
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        try:
            subprocess.run(cmd, env=env, check=True)
        except Exception as e:
            return HttpResponse(f'Erro ao gerar backup: {e}'.encode(), status=500)
        response = FileResponse(open(tmpfile.name, 'rb'), as_attachment=True, filename=f'{db_name}.backup')
        return response

@staff_member_required
def backup_media(request):
    """Compacta a pasta de mídia e serve para download"""
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        return HttpResponse('Pasta de mídia não encontrada.'.encode('utf-8'), status=404)
    with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmpfile:
        tmpfile.close()
        try:
            shutil.make_archive(tmpfile.name[:-7], 'gztar', media_root)
            tar_path = tmpfile.name[:-7] + '.tar.gz'
        except Exception as e:
            return HttpResponse(f'Erro ao compactar mídia: {e}'.encode(), status=500)
        response = FileResponse(open(tar_path, 'rb'), as_attachment=True, filename='media_backup.tar.gz')
        return response

@staff_member_required
@require_http_methods(["GET", "POST"])
def restore_database(request):
    """Recebe upload de backup e restaura o banco PostgreSQL"""
    if request.method == 'POST' and request.FILES.get('backup_file'):
        backup_file = request.FILES['backup_file']
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_host = settings.DATABASES['default'].get('HOST', 'localhost')
        db_port = str(settings.DATABASES['default'].get('PORT', '5432'))
        db_password = settings.DATABASES['default'].get('PASSWORD', '')
        with tempfile.NamedTemporaryFile(suffix='.backup', delete=False) as tmpfile:
            for chunk in backup_file.chunks():
                tmpfile.write(chunk)
            tmpfile.close()
            cmd = [
                'pg_restore',
                '-U', db_user,
                '-h', db_host,
                '-p', db_port,
                '-d', db_name,
                '-c',  # drop objects before recreating
                tmpfile.name
            ]
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            try:
                subprocess.run(cmd, env=env, check=True)
            except Exception as e:
                return HttpResponse(f'Erro ao restaurar backup: {e}'.encode('utf-8'), status=500)
        return HttpResponse('Restauração do banco concluída com sucesso!'.encode('utf-8'))
    return render(request, 'config/restore_database_form.html')

@staff_member_required
@require_http_methods(["GET", "POST"])
def restore_media(request):
    """Recebe upload de arquivo tar.gz e restaura a pasta de mídia"""
    if request.method == 'POST' and request.FILES.get('media_file'):
        media_file = request.FILES['media_file']
        media_root = settings.MEDIA_ROOT
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmpfile:
            for chunk in media_file.chunks():
                tmpfile.write(chunk)
            tmpfile.close()
            try:
                # Extrai o tar.gz para a pasta de mídia
                shutil.unpack_archive(tmpfile.name, media_root)
            except Exception as e:
                return HttpResponse(f'Erro ao restaurar mídia: {e}'.encode('utf-8'), status=500)
        return HttpResponse('Restauração da mídia concluída com sucesso!'.encode('utf-8'))
    return render(request, 'config/restore_media_form.html') 