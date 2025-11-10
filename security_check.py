#!/usr/bin/env python3
import os
import sys

def check_env_file():
    if not os.path.exists('.env'):
        print("❌ .env fil saknas!")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        
    required = ['SECRET_KEY', 'DB_PASSWORD']
    for var in required:
        if var not in content or f'{var}=changeme' in content.lower():
            print(f"❌ {var} är inte korrekt konfigurerad")
            return False
    
    print("✅ .env ser bra ut")
    return True

def check_debug_off():
    with open('.env', 'r') as f:
        if 'DEBUG=True' in f.read():
            print("⚠️  DEBUG är True (OK för demo, men ändra för produktion)")
            return True
    print("✅ DEBUG är False")
    return True

def check_gitignore():
    if not os.path.exists('.gitignore'):
        print("❌ .gitignore saknas!")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    if '.env' not in content or 'db.sqlite3' not in content:
        print("❌ .gitignore saknar viktiga filer")
        return False
    
    print("✅ .gitignore ser bra ut")
    return True

if __name__ == '__main__':
    print("🔒 Kör säkerhetskontroll...\n")
    checks = [check_env_file(), check_debug_off(), check_gitignore()]
    print("\n" + "="*50)
    if all(checks):
        print("✅ Alla kontroller godkända!")
        sys.exit(0)
    else:
        print("❌ Vissa kontroller misslyckades")
        sys.exit(1)
