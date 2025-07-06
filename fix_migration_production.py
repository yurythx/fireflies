#!/usr/bin/env python3
"""
Script para corrigir problema de migração em produção
Resolve o erro: column articles_article.image_caption does not exist

Uso:
    python fix_migration_production.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def setup_django():
    """Configura o Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

def check_migration_status():
    """Verifica o status das migrações"""
    print("🔍 Verificando status das migrações...")
    
    try:
        # Verificar migrações aplicadas
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT app, name FROM django_migrations 
                WHERE app = 'articles' 
                ORDER BY id
            """)
            applied_migrations = cursor.fetchall()
            
        print(f"✅ Migrações aplicadas do app 'articles':")
        for app, name in applied_migrations:
            print(f"   - {app}.{name}")
            
        # Verificar se a migração problemática foi aplicada
        migration_0003_applied = any(name == '0003_article_image_caption' for _, name in applied_migrations)
        
        if migration_0003_applied:
            print("✅ Migração 0003_article_image_caption já foi aplicada")
            return True
        else:
            print("❌ Migração 0003_article_image_caption NÃO foi aplicada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar migrações: {e}")
        return False

def check_column_exists():
    """Verifica se a coluna image_caption existe"""
    print("🔍 Verificando se a coluna image_caption existe...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'articles_article' 
                AND column_name = 'image_caption'
            """)
            result = cursor.fetchone()
            
        if result:
            print("✅ Coluna 'image_caption' existe na tabela")
            return True
        else:
            print("❌ Coluna 'image_caption' NÃO existe na tabela")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar coluna: {e}")
        return False

def apply_migration():
    """Aplica a migração específica"""
    print("🚀 Aplicando migração 0003_article_image_caption...")
    
    try:
        # Executar a migração específica
        execute_from_command_line(['manage.py', 'migrate', 'articles', '0003_article_image_caption'])
        print("✅ Migração aplicada com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao aplicar migração: {e}")
        return False

def create_column_manually():
    """Cria a coluna manualmente se a migração falhar"""
    print("🔧 Criando coluna manualmente...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE articles_article 
                ADD COLUMN image_caption VARCHAR(255) DEFAULT '' 
                NOT NULL
            """)
            
        print("✅ Coluna criada manualmente!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar coluna manualmente: {e}")
        return False

def mark_migration_as_applied():
    """Marca a migração como aplicada no Django"""
    print("📝 Marcando migração como aplicada...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('articles', '0003_article_image_caption', NOW())
                ON CONFLICT (app, name) DO NOTHING
            """)
            
        print("✅ Migração marcada como aplicada!")
        return True
    except Exception as e:
        print(f"❌ Erro ao marcar migração: {e}")
        return False

def test_articles_view():
    """Testa se a view de artigos funciona"""
    print("🧪 Testando view de artigos...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        response = client.get('/artigos/')
        
        if response.status_code == 200:
            print("✅ View de artigos funcionando corretamente!")
            return True
        else:
            print(f"❌ View de artigos retornou status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar view: {e}")
        return False

def main():
    """Função principal"""
    print("🦟 FireFlies - Correção de Migração em Produção")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Verificar status atual
    migration_applied = check_migration_status()
    column_exists = check_column_exists()
    
    print("\n📊 Status Atual:")
    print(f"   Migração aplicada: {'✅' if migration_applied else '❌'}")
    print(f"   Coluna existe: {'✅' if column_exists else '❌'}")
    
    # Se tudo está OK, não precisa fazer nada
    if migration_applied and column_exists:
        print("\n🎉 Tudo está funcionando corretamente!")
        return
    
    print("\n🔧 Iniciando correção...")
    
    # Cenário 1: Migração não aplicada, coluna não existe
    if not migration_applied and not column_exists:
        print("\n📋 Cenário 1: Aplicar migração normalmente")
        if apply_migration():
            print("✅ Problema resolvido!")
        else:
            print("⚠️ Migração falhou, tentando criar coluna manualmente...")
            if create_column_manually() and mark_migration_as_applied():
                print("✅ Problema resolvido manualmente!")
            else:
                print("❌ Falha na correção manual")
                return
    
    # Cenário 2: Migração não aplicada, mas coluna existe
    elif not migration_applied and column_exists:
        print("\n📋 Cenário 2: Coluna existe mas migração não aplicada")
        if mark_migration_as_applied():
            print("✅ Problema resolvido!")
        else:
            print("❌ Falha ao marcar migração como aplicada")
            return
    
    # Cenário 3: Migração aplicada, mas coluna não existe
    elif migration_applied and not column_exists:
        print("\n📋 Cenário 3: Migração aplicada mas coluna não existe")
        if create_column_manually():
            print("✅ Problema resolvido!")
        else:
            print("❌ Falha ao criar coluna")
            return
    
    # Testar se tudo está funcionando
    print("\n🧪 Testando correção...")
    if test_articles_view():
        print("\n🎉 Correção concluída com sucesso!")
        print("✅ A aplicação deve estar funcionando normalmente agora.")
    else:
        print("\n⚠️ Correção aplicada, mas teste falhou.")
        print("🔍 Verifique os logs para mais detalhes.")

if __name__ == "__main__":
    main() 