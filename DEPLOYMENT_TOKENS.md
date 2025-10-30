# Deployment Authentication Tokens

**IMPORTANT:** Keep these tokens secure! Do not share publicly or commit to public repositories.

## 🔐 Vercel Deployment Token

**Token:** `rxvgD8VLh2ezzObeq7I65dsS`

**Usage:**
```bash
# Deploy to Vercel
cd /home/peteylinux/Projects/kevcal-marketing
VERCEL_TOKEN=rxvgD8VLh2ezzObeq7I65dsS npx vercel --prod --token rxvgD8VLh2ezzObeq7I65dsS --yes

# List deployments
VERCEL_TOKEN=rxvgD8VLh2ezzObeq7I65dsS npx vercel ls --token rxvgD8VLh2ezzObeq7I65dsS

# View logs
npx vercel logs https://kevcal-marketing.vercel.app --token rxvgD8VLh2ezzObeq7I65dsS
```

**Project:**
- Name: `kevcal-marketing`
- Production URL: https://kevcal-marketing.vercel.app
- Organization: peter-skottes-projects

**Token Location:**
- Stored in: Vercel Account → Settings → Tokens
- Scope: Full access to all projects

---

## 🚀 Fly.io Authentication Token

**Token:**
```
FlyV1 fm2_lJPECAAAAAAACrzQxBBv/JmI7/FmYJjskKutPG0+wrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABRAwR8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDxUmQaQfPQMzjksbYfGWJId8/uvFnoqH6+3JGlO3QSBx1LkBxQm60L2XVow9VZ4wG8UxmXXMmXQposfO5rETr189+WhlUZPZi7VMD6D3NoLH3poJkeE3BNvV0y7sMDr3hmE/UFO0RBUH9ufKHK5roEO1iB8j7IMx5qREv0gyQPt48RjLhwFYiwBKisOfQ2SlAORgc4Aqt+JHwWRgqdidWlsZGVyH6J3Zx8BxCDt4MJfi6hHZd5yS3IMRwgG91UJZt5gIki/Qre5upSAeA==,fm2_lJPETr189+WhlUZPZi7VMD6D3NoLH3poJkeE3BNvV0y7sMDr3hmE/UFO0RBUH9ufKHK5roEO1iB8j7IMx5qREv0gyQPt48RjLhwFYiwBKisOfcQQAVPSVKc6ViH3zXnfu3S8/MO5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5pAuPAzwAAAAEk+wHeF84AE3RTCpHOABN0UwzEEES0ADWGArt+Xnay//dzxrzEIC2zqAJBP5wXceclGgsVKRMbOlKKERT5gIXvyQC5m/4U
```

**Setup:**
```bash
# Add token to config
mkdir -p /root/.fly
cat > /root/.fly/config.yml << 'EOF'
access_token: FlyV1 fm2_lJPECAAAAAAACrzQxBBv/JmI7/FmYJjskKutPG0+wrVodHRwczovL2FwaS5mbHkuaW8vdjGWAJLOABRAwR8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDxUmQaQfPQMzjksbYfGWJId8/uvFnoqH6+3JGlO3QSBx1LkBxQm60L2XVow9VZ4wG8UxmXXMmXQposfO5rETr189+WhlUZPZi7VMD6D3NoLH3poJkeE3BNvV0y7sMDr3hmE/UFO0RBUH9ufKHK5roEO1iB8j7IMx5qREv0gyQPt48RjLhwFYiwBKisOfQ2SlAORgc4Aqt+JHwWRgqdidWlsZGVyH6J3Zx8BxCDt4MJfi6hHZd5yS3IMRwgG91UJZt5gIki/Qre5upSAeA==,fm2_lJPETr189+WhlUZPZi7VMD6D3NoLH3poJkeE3BNvV0y7sMDr3hmE/UFO0RBUH9ufKHK5roEO1iB8j7IMx5qREv0gyQPt48RjLhwFYiwBKisOfcQQAVPSVKc6ViH3zXnfu3S8/MO5aHR0cHM6Ly9hcGkuZmx5LmlvL2FhYS92MZgEks5pAuPAzwAAAAEk+wHeF84AE3RTCpHOABN0UwzEEES0ADWGArt+Xnay//dzxrzEIC2zqAJBP5wXceclGgsVKRMbOlKKERT5gIXvyQC5m/4U
EOF

# Add Fly.io CLI to PATH
export PATH="/root/.fly/bin:$PATH"

# Verify authentication
flyctl auth whoami
```

**Usage:**
```bash
# Deploy app
export PATH="/root/.fly/bin:$PATH"
flyctl deploy -a hunkofthemonth

# View status
flyctl status -a hunkofthemonth

# View logs
flyctl logs -a hunkofthemonth

# Set secrets
flyctl secrets set SECRET_NAME=value -a hunkofthemonth

# List secrets
flyctl secrets list -a hunkofthemonth

# SSH into machine
flyctl ssh console -a hunkofthemonth
```

**App Details:**
- App Name: `hunkofthemonth`
- Production URL: https://hunkofthemonth.fly.dev
- Organization: personal (Peter Skotte)
- Region: sjc (San Jose, CA)
- Machines: 2x shared CPU (512MB RAM each)

---

## 🔒 Environment Variables (Fly.io)

**Current Secrets:**
```bash
FLASK_SECRET_KEY     # Auto-generated secure key
GOOGLE_API_KEY       # AIzaSyAXdQlDioxbG3wr9jHEaFJiIt6AB5Bdals
FLASK_ENV            # production
```

**To update:**
```bash
flyctl secrets set GOOGLE_API_KEY=AIzaSyAXdQlDioxbG3wr9jHEaFJiIt6AB5Bdals -a hunkofthemonth
```

---

## 📦 Deployment Workflows

### Deploy Flask Backend (Fly.io):
```bash
cd /home/peteylinux/Projects/KevCal
git add .
git commit -m "Your changes"
git push origin main

export PATH="/root/.fly/bin:$PATH"
flyctl deploy -a hunkofthemonth
```

### Deploy Static Frontend (Vercel):
```bash
cd /home/peteylinux/Projects/kevcal-marketing
# Make changes to public/index.html or vercel.json

VERCEL_TOKEN=rxvgD8VLh2ezzObeq7I65dsS npx vercel --prod --token rxvgD8VLh2ezzObeq7I65dsS --yes
```

---

## 🔗 Live URLs

- **Frontend:** https://kevcal-marketing.vercel.app (Vercel)
- **Backend API:** https://hunkofthemonth.fly.dev (Fly.io)
- **GitHub Repo:** https://github.com/IncrediblyHungie/HunkOfTheMonth

---

## 📝 Token Security Notes

1. **Never commit these tokens to public repositories**
2. **Never share tokens in screenshots or documentation**
3. **Rotate tokens if compromised**
4. **Use environment variables in CI/CD pipelines**

**To rotate tokens:**
- **Vercel:** Visit https://vercel.com/account/tokens → Revoke old token → Create new token
- **Fly.io:** Run `flyctl auth token` to get a new token, or login again with `flyctl auth login`

---

*Last updated: 2025-10-29*
*Keep this file in a secure location, do NOT commit to public repos*
