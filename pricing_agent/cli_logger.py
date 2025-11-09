import time

class CLIPrinter:
    @staticmethod
    def info(msg): print(f"→ {msg}")
    @staticmethod
    def success(msg): print(f"✅ {msg}\n")
    @staticmethod
    def section(title): print(f"\n📦 {title}")
    @staticmethod
    def save(path): print(f"💾 Saving output → {path}")
    @staticmethod
    def done(msg="Operation completed!"): 
        print(f"✅ {msg}\n"); time.sleep(0.3)
