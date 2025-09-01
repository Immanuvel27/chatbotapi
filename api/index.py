from main import app
from mangum import Mangum

# 👇 Vercel expects this handler
handler = Mangum(app)
