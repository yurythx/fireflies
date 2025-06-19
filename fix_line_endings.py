#!/usr/bin/env python3
"""
Script para corrigir line endings em arquivos shell
"""

import os

def fix_line_endings(file_path):
    """Corrige line endings de CRLF para LF"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substituir CRLF por LF
        content = content.replace('\r\n', '\n')
        
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✅ Corrigido: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao corrigir {file_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 Corrigindo line endings em scripts shell...")
    
    # Arquivos para corrigir
    files_to_fix = [
        'docker/entrypoint.sh',
        'docker/start.sh',
        'create_env_file.sh',
        'deploy_improved.sh',
        'reset_database.sh',
        'fix_deploy_issues.sh',
        'setup_ubuntu_deploy.sh',
        'cleanup_unused_files.sh'
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_line_endings(file_path):
                fixed_count += 1
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
    
    print(f"\n✅ Processo concluído! {fixed_count} arquivos corrigidos.")
    print("🚀 Agora você pode reconstruir os containers:")
    print("   docker-compose down")
    print("   docker-compose build --no-cache")
    print("   docker-compose up -d")

if __name__ == "__main__":
    main() 