import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/blackrose.db")
SECRET_KEY = os.getenv("SECRET_KEY", "Rx9#Lzm8!Kp3@Qw")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

FOUNDER_TY_EMAIL = os.getenv("FOUNDER_TY_EMAIL", "NacktGem@proton.me")
FOUNDER_TY_PASSWORD = os.getenv("FOUNDER_TY_PASSWORD", "Rx9#Lzm8!Kp3@Qw")
FOUNDER_JULES_EMAIL = os.getenv("FOUNDER_JULES_EMAIL", "jamminjuless@proton.me")
FOUNDER_JULES_PASSWORD = os.getenv("FOUNDER_JULES_PASSWORD", "Elikyce2!")

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://blackrosecollective.studio")
ERROR_LOG_PATH = os.getenv("ERROR_LOG_PATH", "/var/log/blackrose/errors.log")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", FRONTEND_URL)
TOR_SOCKS_PROXY = os.getenv("TOR_SOCKS_PROXY", "")

DIGITALOCEAN_API = os.getenv("DIGITALOCEAN_API", "dop_v1_ecf810a9351d5601833cba637b452c36b5ef551fe4cb7bbd17c44f36201687b1")
CLOUDFLARE_API = os.getenv("CLOUDFLARE_API", "8c15c52beffd1bccfa19586c97ea9310c0fe4")
CLOUDFLARE_USERNAME = os.getenv("CLOUDFLARE_USERNAME", "nacktgem@proton.me")
CLOUDFLARE_PASSWORD = os.getenv("CLOUDFLARE_PASSWORD", "Rx9#Lzm8!Kp3@Qw")
DIGITALOCEAN_USERNAME = os.getenv("DIGITALOCEAN_USERNAME", "nacktgem@proton.me")
DIGITALOCEAN_PASSWORD = os.getenv("DIGITALOCEAN_PASSWORD", "Rx9#Lzm8!Kp3@Qw")

NAMECHEAP_USERNAME = os.getenv("NAMECHEAP_USERNAME", "blackrosecollective")
NAMECHEAP_PASSWORD = os.getenv("NAMECHEAP_PASSWORD", "Rx9#Lzm8!")

BLACKROSE_ADMIN_EMAIL = os.getenv("BLACKROSE_ADMIN_EMAIL", "black.rose.collective@proton.me")
BLACKROSE_ADMIN_PASSWORD = os.getenv("BLACKROSE_ADMIN_PASSWORD", "Rx9#Lzm8!Kp3@Qw")
BLACKROSE_EXTRA_PASSWORD = os.getenv("BLACKROSE_EXTRA_PASSWORD", "Rx9#Lzm8!")

NACKTGEM_EMAIL = os.getenv("NACKTGEM_EMAIL", "NacktGem@proton.me")
NACKTGEM_PASSWORD = os.getenv("NACKTGEM_PASSWORD", "Rx9#Lzm8!Kp3@Qw")
SEKT_RANCH_EMAIL = os.getenv("SEKT_RANCH_EMAIL", "sekt.ranch@proton.me")
SEKT_RANCH_PASSWORD = os.getenv("SEKT_RANCH_PASSWORD", "Rx9#Lzm8!Kp3@Qw")
FOURLEPORTAL_EMAIL = os.getenv("FOURLEPORTAL_EMAIL", "4LEportal@proton.me")
FOURLEPORTAL_PASSWORD = os.getenv("FOURLEPORTAL_PASSWORD", "Rx9#Lzm8!Kp3@Qw")
JULIE_EMAIL = os.getenv("JULIE_EMAIL", "jamminjuless@proton.me")
JULIE_PASSWORD = os.getenv("JULIE_PASSWORD", "Elikyce2!")
FACEBOOK_USERNAME = os.getenv("FACEBOOK_USERNAME", "3375638770")
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD", "Sparrow3120")
X_USERNAME = os.getenv("X_USERNAME", "b_rose_collect")
X_PASSWORD = os.getenv("X_PASSWORD", "Rx9#Lzm8!")
ONLYFANS_USERNAME = os.getenv("ONLYFANS_USERNAME", "nacktgem@gmail.com")
ONLYFANS_PASSWORD = os.getenv("ONLYFANS_PASSWORD", "Nudist3120")
EXTRA_PASSWORD = os.getenv("EXTRA_PASSWORD", "NovaCore!2025@BlackRose")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
