from getpass import getpass
from passlib.context import CryptContext
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")
p=getpass("Nueva contraseña DataAI: ")
q=getpass("Repita contraseña: ")
if p!=q or len(p)<10: raise SystemExit("Las contraseñas no coinciden o tienen menos de 10 caracteres.")
print("\nDATAAI_ADMIN_PASSWORD_HASH="+pwd.hash(p))
