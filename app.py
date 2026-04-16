import streamlit as st
import torch, torch.nn as nn
import numpy as np
from PIL import Image
import io, uuid, os
from supabase import create_client
from crypto_utils import generate_stego_id, encrypt_image_bytes, decrypt_image_bytes

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Deep-Stego Secure", page_icon="🔐", layout="wide",
                   initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#07060b}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding-top:1.5rem;padding-bottom:2rem;max-width:1200px}

/* ─── Animated gradient bg ─── */
.stApp{background:linear-gradient(135deg,#07060b 0%,#0d0b1a 40%,#12101f 60%,#07060b 100%)}

/* ─── Hero ─── */
.hero{
    background:linear-gradient(160deg,rgba(99,60,255,0.12),rgba(45,20,120,0.15),rgba(0,210,190,0.08));
    border:1px solid rgba(120,80,255,0.15);border-radius:28px;
    padding:3.5rem 2rem 3rem;text-align:center;margin-bottom:2.5rem;
    position:relative;overflow:hidden;
    box-shadow:0 0 80px rgba(99,60,255,0.08),inset 0 1px 0 rgba(255,255,255,0.05);
}
.hero::before{content:'';position:absolute;top:-100%;left:-50%;width:200%;height:300%;
background:conic-gradient(from 180deg,transparent,rgba(99,60,255,0.04),transparent 40%);
animation:hero-spin 12s linear infinite}
@keyframes hero-spin{100%{transform:rotate(360deg)}}
.hero::after{content:'';position:absolute;inset:0;border-radius:28px;
background:radial-gradient(ellipse at 30% 0%,rgba(99,60,255,0.08),transparent 60%)}
.hero h1{
    font-size:3.2rem;font-weight:900;letter-spacing:-0.03em;
    background:linear-gradient(135deg,#c084fc,#818cf8,#38bdf8,#34d399);background-size:200% 200%;
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:gradient-shift 6s ease infinite;margin-bottom:.5rem;position:relative;z-index:1;
}
@keyframes gradient-shift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.hero .subtitle{color:rgba(255,255,255,0.5);font-size:1rem;font-weight:300;
line-height:1.6;position:relative;z-index:1;max-width:600px;margin:0 auto}
.badge-row{display:flex;justify-content:center;gap:12px;margin-top:1.8rem;
flex-wrap:wrap;position:relative;z-index:1}
.tech-badge{
    background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
    border-radius:100px;padding:6px 16px;font-size:.78rem;font-weight:500;
    color:rgba(255,255,255,0.6);backdrop-filter:blur(10px);
    transition:all .3s;display:flex;align-items:center;gap:6px;
}
.tech-badge:hover{border-color:rgba(120,80,255,0.4);background:rgba(120,80,255,0.08)}
.tech-badge .dot{width:6px;height:6px;border-radius:50%;display:inline-block}
.dot-purple{background:#a78bfa}.dot-blue{background:#60a5fa}.dot-green{background:#34d399}.dot-amber{background:#fbbf24}

/* ─── Auth Container ─── */
.auth-wrapper{
    max-width:480px;margin:0 auto;
    background:linear-gradient(180deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01));
    border:1px solid rgba(255,255,255,0.06);border-radius:24px;
    padding:2.5rem 2rem;backdrop-filter:blur(20px);
    box-shadow:0 25px 80px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.04);
    position:relative;overflow:hidden;
}
.auth-wrapper::before{content:'';position:absolute;top:0;left:20%;right:20%;height:1px;
background:linear-gradient(90deg,transparent,rgba(120,80,255,0.5),transparent)}
.auth-title{font-size:1.5rem;font-weight:700;color:white;margin-bottom:.3rem;letter-spacing:-0.02em}
.auth-sub{color:rgba(255,255,255,0.35);font-size:.88rem;margin-bottom:1.5rem;font-weight:300}
.auth-divider{display:flex;align-items:center;gap:12px;margin:1.5rem 0;color:rgba(255,255,255,0.2);font-size:.8rem}
.auth-divider::before,.auth-divider::after{content:'';flex:1;height:1px;background:rgba(255,255,255,0.08)}
.feature-pill{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(99,60,255,0.08);border:1px solid rgba(99,60,255,0.2);
    border-radius:100px;padding:8px 16px;font-size:.8rem;
    color:rgba(255,255,255,0.6);margin:4px;
}

/* ─── Glass Cards ─── */
.glass-card{
    background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:20px;padding:1.5rem;margin-bottom:1rem;
    backdrop-filter:blur(10px);transition:all .3s;
    box-shadow:0 4px 30px rgba(0,0,0,0.1);
}
.glass-card:hover{border-color:rgba(120,80,255,0.2);background:rgba(255,255,255,0.03)}

/* ─── User Bar ─── */
.user-bar{
    display:flex;align-items:center;justify-content:space-between;
    background:linear-gradient(135deg,rgba(99,60,255,0.06),rgba(56,189,248,0.04));
    border:1px solid rgba(255,255,255,0.06);border-radius:16px;
    padding:12px 20px;margin-bottom:1.5rem;
}
.user-info{display:flex;align-items:center;gap:12px}
.user-avatar{
    width:42px;height:42px;border-radius:14px;
    background:linear-gradient(135deg,#7c3aed,#2563eb);
    display:flex;align-items:center;justify-content:center;font-size:1.2rem;
    box-shadow:0 4px 15px rgba(99,60,255,0.3);
}
.user-name{font-weight:700;color:white;font-size:.95rem;letter-spacing:-0.01em}
.user-id{font-size:.72rem;color:rgba(255,255,255,0.35);font-family:'JetBrains Mono',monospace}
.shield-badge{
    display:flex;align-items:center;gap:6px;
    background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);
    border-radius:100px;padding:5px 14px;font-size:.75rem;color:#34d399;font-weight:500;
}

/* ─── Section Headers ─── */
.section-header{display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;
padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.06)}
.section-header h2{font-size:1.3rem;font-weight:700;color:white;margin:0;letter-spacing:-0.02em}
.section-header .icon{font-size:1.4rem}

/* ─── Message Cards ─── */
.msg-card{
    background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
    border-radius:16px;padding:16px 20px;margin-bottom:10px;transition:all .3s;
}
.msg-card:hover{border-color:rgba(120,80,255,0.2);transform:translateY(-1px);
box-shadow:0 8px 30px rgba(0,0,0,0.2)}
.msg-card.unread{border-left:3px solid #a78bfa}
.msg-card.read{border-left:3px solid rgba(255,255,255,0.08);opacity:.7}
.msg-meta{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.sender-tag{font-size:.85rem;font-weight:600;color:#818cf8}
.date-tag{font-size:.78rem;color:rgba(255,255,255,0.3)}
.status-tag{font-size:.7rem;padding:3px 10px;border-radius:100px;font-weight:600;letter-spacing:.02em}
.status-unread{background:rgba(167,139,250,0.15);color:#a78bfa}
.status-read{background:rgba(52,211,153,0.12);color:#34d399}
.lock-tag{background:rgba(251,191,36,0.12);color:#fbbf24;font-size:.7rem;
padding:3px 10px;border-radius:100px;font-weight:600}

/* ─── Metrics ─── */
.metric-row{display:flex;gap:12px;margin:1rem 0;flex-wrap:wrap}
.metric-card{
    flex:1;min-width:100px;background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.06);border-radius:16px;
    padding:16px;text-align:center;transition:all .3s;
}
.metric-card:hover{border-color:rgba(120,80,255,0.2)}
.metric-val{font-size:1.6rem;font-weight:800;color:#a78bfa;letter-spacing:-0.02em}
.metric-lbl{font-size:.68rem;color:rgba(255,255,255,0.35);margin-top:4px;
text-transform:uppercase;letter-spacing:.08em;font-weight:600}
.img-label{text-align:center;font-size:.75rem;color:rgba(255,255,255,0.4);
margin-top:6px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}

/* ─── Banners ─── */
.success-banner{
    background:linear-gradient(135deg,rgba(52,211,153,0.1),rgba(16,185,129,0.06));
    border:1px solid rgba(52,211,153,0.25);border-radius:16px;
    padding:14px 20px;color:#34d399;font-weight:500;
    margin:1rem 0;display:flex;align-items:center;gap:10px;
}
.error-banner{
    background:linear-gradient(135deg,rgba(239,68,68,0.1),rgba(220,38,38,0.06));
    border:1px solid rgba(239,68,68,0.25);border-radius:16px;
    padding:14px 20px;color:#ef4444;font-weight:500;margin:1rem 0;
}
.info-banner{
    background:rgba(99,60,255,0.06);border:1px solid rgba(99,60,255,0.15);
    border-radius:16px;padding:14px 20px;
    color:rgba(255,255,255,0.6);font-size:.88rem;margin:1rem 0;line-height:1.6;
}
.profile-id{
    background:linear-gradient(135deg,rgba(99,60,255,0.08),rgba(56,189,248,0.06));
    border:1px solid rgba(99,60,255,0.2);border-radius:20px;
    padding:24px;text-align:center;margin:1rem 0;
    box-shadow:0 0 60px rgba(99,60,255,0.06);
}
.profile-id .id-val{font-size:2.2rem;font-weight:900;color:#a78bfa;
font-family:'JetBrains Mono',monospace;letter-spacing:.2em}
.profile-id .id-lbl{font-size:.72rem;color:rgba(255,255,255,0.35);margin-top:6px;
text-transform:uppercase;letter-spacing:.1em;font-weight:600}

/* ─── Buttons ─── */
div.stButton>button{
    border-radius:12px!important;font-weight:600!important;
    font-family:'Inter',sans-serif!important;transition:all .25s!important;
    letter-spacing:.01em!important;
}
div.stButton>button:hover{transform:translateY(-2px)!important;
box-shadow:0 8px 25px rgba(99,60,255,0.25)!important}
div.stButton>button[kind="primary"]{
    background:linear-gradient(135deg,#7c3aed,#6366f1,#2563eb)!important;
    border:none!important;box-shadow:0 4px 15px rgba(99,60,255,0.3)!important;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"]{gap:4px;background:rgba(255,255,255,0.02);
border-radius:14px;padding:4px;border:1px solid rgba(255,255,255,0.05)}
.stTabs [data-baseweb="tab"]{border-radius:10px!important;padding:10px 24px!important;
font-weight:500!important;font-size:.88rem!important;transition:all .2s!important}
.stTabs [aria-selected="true"]{background:rgba(99,60,255,0.15)!important;
color:#c084fc!important;font-weight:600!important}
.stTabs [data-baseweb="tab-highlight"]{background:transparent!important}

/* ─── Inputs ─── */
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
    background:rgba(255,255,255,0.03)!important;border:1px solid rgba(255,255,255,0.08)!important;
    border-radius:12px!important;color:white!important;font-family:'Inter',sans-serif!important;
    transition:all .2s!important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{
    border-color:rgba(99,60,255,0.5)!important;box-shadow:0 0 20px rgba(99,60,255,0.1)!important;
}
.stSelectbox>div>div{background:rgba(255,255,255,0.03)!important;
border:1px solid rgba(255,255,255,0.08)!important;border-radius:12px!important}
.stFileUploader{border:2px dashed rgba(255,255,255,0.08)!important;
border-radius:16px!important;background:rgba(255,255,255,0.01)!important}
.stCheckbox label span{color:rgba(255,255,255,0.7)!important}

/* ─── Scrollbar ─── */
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(99,60,255,0.3);border-radius:3px}
</style>""", unsafe_allow_html=True)

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPA_URL = os.environ.get("SUPABASE_URL", "https://uptkoxuoppvcyfnqvmfj.supabase.co")
SUPA_KEY = os.environ.get("SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVwdGtveHVvcHB2Y3lmbnF2bWZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ3Njk5NDIsImV4cCI6MjA5MDM0NTk0Mn0.ZfddbXl7QiaQQ1ddg9rJBodRpT-Fql9IIxk1HKgfrsY")
sb = create_client(SUPA_URL, SUPA_KEY)

# Restore auth session on Streamlit rerun (critical for RLS)
if "_sb_access_token" in st.session_state and "_sb_refresh_token" in st.session_state:
    try:
        sb.auth.set_session(st.session_state["_sb_access_token"], st.session_state["_sb_refresh_token"])
    except Exception:
        pass  # Token expired — user will need to re-login

# ── Model ─────────────────────────────────────────────────────────────────────
IMG_SIZE = 128
DEVICE = torch.device("cpu")

class ConvBlock(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.b = nn.Sequential(nn.Conv2d(i,o,3,1,1,bias=False), nn.BatchNorm2d(o), nn.ReLU(True))
    def forward(self, x): return self.b(x)

class UNet(nn.Module):
    def __init__(self, ic=6, oc=3, bf=64):
        super().__init__()
        self.e1=nn.Sequential(ConvBlock(ic,bf),ConvBlock(bf,bf))
        self.e2=nn.Sequential(ConvBlock(bf,bf*2),ConvBlock(bf*2,bf*2))
        self.e3=nn.Sequential(ConvBlock(bf*2,bf*4),ConvBlock(bf*4,bf*4))
        self.e4=nn.Sequential(ConvBlock(bf*4,bf*8),ConvBlock(bf*8,bf*8))
        self.bn=nn.Sequential(ConvBlock(bf*8,bf*8),ConvBlock(bf*8,bf*8))
        self.d4=nn.Sequential(ConvBlock(bf*16,bf*8),ConvBlock(bf*8,bf*4))
        self.d3=nn.Sequential(ConvBlock(bf*8,bf*4),ConvBlock(bf*4,bf*2))
        self.d2=nn.Sequential(ConvBlock(bf*4,bf*2),ConvBlock(bf*2,bf))
        self.d1=nn.Sequential(ConvBlock(bf*2,bf),ConvBlock(bf,bf//2))
        self.out=nn.Sequential(nn.Conv2d(bf//2,oc,1),nn.Sigmoid())
        self.pool=nn.MaxPool2d(2); self.up=nn.Upsample(scale_factor=2,mode='bilinear',align_corners=True)
    def forward(self, x):
        e1=self.e1(x);e2=self.e2(self.pool(e1));e3=self.e3(self.pool(e2));e4=self.e4(self.pool(e3))
        b=self.bn(self.pool(e4))
        return self.out(self.d1(torch.cat([self.up(self.d2(torch.cat([self.up(self.d3(torch.cat([self.up(self.d4(torch.cat([self.up(b),e4],1))),e3],1))),e2],1))),e1],1)))

class HidingNet(nn.Module):
    def __init__(self, bf=64): super().__init__(); self.u=UNet(6,3,bf)
    def forward(self, c, s): return self.u(torch.cat([c,s],1))

class RevealNet(nn.Module):
    def __init__(self, bf=64): super().__init__(); self.u=UNet(3,3,bf)
    def forward(self, x): return self.u(x)

@st.cache_resource(show_spinner=False)
def load_models():
    h=HidingNet(64).to(DEVICE); r=RevealNet(64).to(DEVICE)
    # Try slim model first (69MB), then full, then HF download
    if os.path.exists("best_slim.pt"): p="best_slim.pt"
    elif os.path.exists("best.pt"): p="best.pt"
    else:
        try:
            from huggingface_hub import hf_hub_download
            repo = os.environ.get("HF_REPO","")
            try: p=hf_hub_download(repo_id=repo,filename="best_slim.pt",local_dir=".")
            except Exception: p=hf_hub_download(repo_id=repo,filename="best.pt",local_dir=".")
        except Exception as e: return None,None,str(e)
    ck=torch.load(p,map_location=DEVICE,weights_only=False)
    # Convert float16 weights to float32 if needed
    def _to_f32(sd): return {k:(v.float() if v.dtype==torch.float16 else v) for k,v in sd.items()}
    h.load_state_dict(_to_f32(ck.get("hiding",ck.get("hiding_net",{})))); r.load_state_dict(_to_f32(ck.get("reveal",ck.get("reveal_net",{}))))
    h.eval(); r.eval(); return h,r,None

# ── Helpers ───────────────────────────────────────────────────────────────────
def preprocess(img):
    img=img.convert("RGB").resize((IMG_SIZE,IMG_SIZE),Image.BICUBIC)
    return torch.from_numpy(np.array(img,dtype=np.float32)/255.0).permute(2,0,1).unsqueeze(0).to(DEVICE)

def postprocess(t):
    return Image.fromarray((t.squeeze(0).detach().cpu().clamp(0,1).permute(1,2,0).numpy()*255).astype(np.uint8))

def to_bytes(img):
    buf=io.BytesIO(); img.save(buf,format="PNG"); return buf.getvalue()

def calc_psnr(a,b):
    mse=np.mean((np.array(a).astype(float)-np.array(b).astype(float))**2)
    return 0 if mse==0 else round(20*np.log10(255/np.sqrt(mse)),1)

def calc_ssim(a,b):
    a,b=np.array(a).astype(float),np.array(b).astype(float)
    ma,mb=a.mean(),b.mean(); sa,sb=a.std(),b.std()
    cov=((a-ma)*(b-mb)).mean(); c1,c2=(0.01*255)**2,(0.03*255)**2
    return round(float((2*ma*mb+c1)*(2*cov+c2)/((ma**2+mb**2+c1)*(sa**2+sb**2+c2))),4)

def detection_score(p,s):
    # SSIM weighted 70% (perceptual), PSNR weighted 30%
    # SSIM 0.99+ is near-perfect; PSNR >20 is acceptable for steganography
    ssim_score = min(max((s - 0.85) / 0.15, 0), 1)  # 0.85→0%, 1.0→100%
    psnr_score = min(max((p - 18) / 22, 0), 1)       # 18→0%, 40→100%
    return round(ssim_score * 70 + psnr_score * 30, 1)

def pixel_diff_heatmap(a,b):
    diff=np.abs(np.array(a).astype(float)-np.array(b).astype(float)).mean(axis=2)
    if diff.max()>0: diff=(diff/diff.max()*255)
    hm=np.zeros((*diff.shape,3),dtype=np.uint8)
    hm[:,:,0]=(diff*0.9).astype(np.uint8)
    hm[:,:,1]=((255-diff)*0.3).astype(np.uint8)
    hm[:,:,2]=(np.clip(200-diff,0,255)*0.7).astype(np.uint8)
    return Image.fromarray(hm)

# ── DB Functions ──────────────────────────────────────────────────────────────
def search_users(q, my_id):
    try:
        r = sb.table("profiles").select("id,username,stego_id") \
            .or_(f"username.ilike.%{q}%,stego_id.ilike.%{q}%") \
            .neq("id", my_id).limit(10).execute()
        return r.data or []
    except Exception as e:
        st.toast(f"Search error: {e}", icon="⚠️")
        return []

def upload_stego(data, fn):
    sb.storage.from_("stego-images").upload(fn, data, {"content-type":"application/octet-stream"})

def insert_message(sid, rid, path, note, has_pp, nonce_b64, salt_b64):
    sb.table("messages").insert({
        "sender_id":sid,"receiver_id":rid,"stego_path":path,"note":note,
        "revealed":False,"passphrase_hash":"yes" if has_pp else "no",
        "encryption_iv":nonce_b64,"sender_public_key":salt_b64
    }).execute()

def get_inbox(uid):
    return (sb.table("messages").select("*, profiles!messages_sender_id_fkey(username,stego_id)")
            .eq("receiver_id",uid).order("created_at",desc=True).execute()).data or []

def get_sent(uid):
    return (sb.table("messages").select("*, profiles!messages_receiver_id_fkey(username,stego_id)")
            .eq("sender_id",uid).order("created_at",desc=True).execute()).data or []

def download_stego(p): return sb.storage.from_("stego-images").download(p)
def mark_revealed(mid): sb.table("messages").update({"revealed":True}).eq("id",mid).execute()

# ── Auth ──────────────────────────────────────────────────────────────────────
def _ensure_profile(user, username=None):
    """Ensure a profile row exists for the given auth user. Creates one if missing."""
    try:
        prof = sb.table("profiles").select("*").eq("id", user.id).single().execute()
        return prof.data
    except Exception:
        # Profile missing — create it
        uname = username or (user.user_metadata or {}).get("username", user.email.split("@")[0])
        sid = generate_stego_id()
        sb.table("profiles").upsert({"id": user.id, "username": uname, "stego_id": sid}).execute()
        prof = sb.table("profiles").select("*").eq("id", user.id).single().execute()
        return prof.data

def do_register(username, email, password):
    try:
        sid = generate_stego_id()
        res = sb.auth.sign_up({"email": email, "password": password,
            "options": {"data": {"username": username}}})
        if not res.user:
            return False, None, "Registration failed."
        # Create profile (upsert handles duplicates gracefully)
        sb.table("profiles").upsert({"id": res.user.id, "username": username, "stego_id": sid}).execute()
        return True, sid, None
    except Exception as e:
        err = str(e)
        if "already registered" in err.lower() or "already been registered" in err.lower():
            # User exists in auth — try to log them in and ensure profile exists
            try:
                login_res = sb.auth.sign_in_with_password({"email": email, "password": password})
                if login_res.user:
                    profile = _ensure_profile(login_res.user, username)
                    return False, None, f"This email is already registered. Your Stego-ID is {profile.get('stego_id','N/A')}. Please sign in instead."
            except Exception:
                pass
            return False, None, "This email is already registered. Please sign in."
        return False, None, err

def do_login(email, password):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            profile = _ensure_profile(res.user)
            st.session_state.user = res.user
            st.session_state.profile = profile
            # Store tokens for session restore on rerun
            if res.session:
                st.session_state["_sb_access_token"] = res.session.access_token
                st.session_state["_sb_refresh_token"] = res.session.refresh_token
            return True, None
        return False, "Login failed."
    except Exception as e: return False, str(e)

def do_logout():
    for k in ["user","profile","stego_result","_sb_access_token","_sb_refresh_token",
              "_passphrase_confirmed","_passphrase_value","_search_results"]:
        if k in st.session_state: st.session_state[k]=None
    try: sb.auth.sign_out()
    except Exception: pass
    st.rerun()

# ── Session ───────────────────────────────────────────────────────────────────
for k in ["user","profile","stego_result"]:
    if k not in st.session_state: st.session_state[k]=None

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""<div class="hero">
<h1>🔐 Deep-Stego Secure</h1>
<p class="subtitle">Military-grade neural image steganography with AES-256 encryption.<br>
Hide secrets inside ordinary images — invisible and unbreakable.</p>
<div class="badge-row">
<div class="tech-badge"><span class="dot dot-purple"></span>Dual U-Net</div>
<div class="tech-badge"><span class="dot dot-blue"></span>AES-256-GCM</div>
<div class="tech-badge"><span class="dot dot-green"></span>128×128 HD</div>
<div class="tech-badge"><span class="dot dot-amber"></span>SSIM &gt;0.92</div>
</div></div>""", unsafe_allow_html=True)

with st.spinner("Loading AI model..."):
    hiding_net, reveal_net, model_error = load_models()
if model_error:
    st.error(f"⚠️ {model_error}"); st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.user is None:
    tab_login, tab_reg = st.tabs(["🔑  Sign In", "✨  Create Account"])

    with tab_login:
        st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Sign in to access your encrypted messages</div>', unsafe_allow_html=True)
        l_email = st.text_input("Email", placeholder="you@email.com", key="le")
        l_pass = st.text_input("Password", type="password", placeholder="Enter your password", key="lp")
        if st.button("Sign In", type="primary", use_container_width=True, key="log_btn"):
            ok, err = do_login(l_email, l_pass)
            if ok: st.rerun()
            else: st.error(err or "Login failed.")
        st.markdown('<div class="auth-divider">secured with Supabase Auth</div>', unsafe_allow_html=True)
        st.markdown("""<div style="display:flex;justify-content:center;flex-wrap:wrap">
        <div class="feature-pill">🔐 E2E Encrypted</div>
        <div class="feature-pill">🧠 AI Powered</div>
        <div class="feature-pill">👁️ Invisible</div>
        </div>""", unsafe_allow_html=True)

    with tab_reg:
        st.markdown('<div class="auth-title">Join Deep-Stego Secure</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Create your account and get a unique Stego-ID</div>', unsafe_allow_html=True)
        r_user = st.text_input("Username", placeholder="john_doe", key="ru")
        r_email = st.text_input("Email", placeholder="you@email.com", key="re")
        r_pass = st.text_input("Password", type="password", placeholder="Min 6 characters", key="rp")
        st.markdown("""<div class="info-banner">
        🛡️ Every account can <b>send</b> and <b>receive</b> secret images.<br>
        You'll get a unique <b>Stego-ID</b> for others to find you.
        </div>""", unsafe_allow_html=True)
        if st.button("Create Account", type="primary", use_container_width=True, key="reg_btn"):
            if all([r_user, r_email, r_pass]):
                ok, sid, err = do_register(r_user, r_email, r_pass)
                if ok:
                    st.markdown(f"""<div class="success-banner">
                    ✅ Account created! Your Stego-ID: <b style="font-family:'JetBrains Mono';font-size:1.1rem">{sid}</b>
                    </div>""", unsafe_allow_html=True)
                    st.info("Now sign in with your credentials.")
                else: st.error(err or "Registration failed.")
            else: st.warning("Please fill all fields.")


    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
profile = st.session_state.profile
uid = profile["id"]; uname = profile["username"]; stego_id = profile.get("stego_id","N/A")

st.markdown(f"""<div class="user-bar">
<div class="user-info">
<div class="user-avatar">👤</div>
<div><div class="user-name">{uname}</div>
<div class="user-id">{stego_id}</div></div>
</div>
<div class="shield-badge">🔐 AES-256 Protected</div>
</div>""", unsafe_allow_html=True)

c_spacer, c_logout = st.columns([6,1])
with c_logout:
    if st.button("🚪 Logout", use_container_width=True): do_logout()

tab_encode, tab_inbox, tab_decode, tab_sent, tab_profile = st.tabs([
    "📤 Encode & Send", "📥 Inbox", "🔓 Decode", "📨 Sent", "👤 Profile"])

# ═══════════════════ ENCODE & SEND ═══════════════════
with tab_encode:
    st.markdown("""<div class="section-header">
    <span class="icon">📤</span><h2>Encode & Send Hidden Image</h2></div>""", unsafe_allow_html=True)

    # ── STEP 1: Upload Images ─────────────────────────────────────────────
    st.markdown("#### 🖼️ Step 1 — Upload Images")
    cc, cs = st.columns(2)
    with cc:
        st.markdown("""<div class="glass-card">
        <div style="color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:8px">
        🖼️ Cover Image <span style="color:rgba(255,255,255,0.25);font-weight:400;font-size:.85rem">
        — what everyone sees</span></div>""", unsafe_allow_html=True)
        cover_f = st.file_uploader("", type=["jpg","jpeg","png"], key="cover", label_visibility="collapsed")
        if cover_f:
            st.image(cover_f, use_container_width=True)
            st.markdown('<div class="img-label">Cover</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with cs:
        st.markdown("""<div class="glass-card">
        <div style="color:rgba(255,255,255,0.7);font-weight:600;margin-bottom:8px">
        🤫 Secret Image <span style="color:rgba(255,255,255,0.25);font-weight:400;font-size:.85rem">
        — what gets hidden</span></div>""", unsafe_allow_html=True)
        secret_f = st.file_uploader("", type=["jpg","jpeg","png"], key="secret", label_visibility="collapsed")
        if secret_f:
            st.image(secret_f, use_container_width=True)
            st.markdown('<div class="img-label">Secret</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── STEP 2: Set Passphrase ────────────────────────────────────────────
    st.markdown("#### 🔒 Step 2 — Set Secret Passphrase")

    # Check if passphrase already set in session
    pp_set = st.session_state.get("_passphrase_confirmed", False)

    if not pp_set:
        pc1, pc2 = st.columns([3, 1])
        with pc1:
            pp_val = st.text_input("Secret passphrase", type="password", key="pp",
                                    placeholder="Enter a strong passphrase...", label_visibility="collapsed")
        with pc2:
            if st.button("🔒 Set Key", use_container_width=True, type="primary"):
                if pp_val and len(pp_val) >= 3:
                    st.session_state["_passphrase_confirmed"] = True
                    st.session_state["_passphrase_value"] = pp_val
                    st.rerun()
                else:
                    st.error("Min 3 characters.")
        st.markdown("""<div class="info-banner">
        🔑 <b>The receiver must know this passphrase</b> to decrypt and reveal the hidden image.
        Share it through a separate secure channel (in-person, phone call, etc).
        </div>""", unsafe_allow_html=True)
    else:
        pp_val = st.session_state.get("_passphrase_value", "")
        st.markdown(f"""<div class="success-banner">
        🔐 Passphrase set! <b>({len(pp_val)} characters)</b> — ready to generate.
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 Change Passphrase"):
            st.session_state["_passphrase_confirmed"] = False
            st.session_state["_passphrase_value"] = ""
            st.rerun()

    # ── STEP 3: Encode ────────────────────────────────────────────────────
    passphrase = st.session_state.get("_passphrase_value", "")
    if cover_f and secret_f and pp_set:
        st.markdown("---")
        if st.button("🧠  Generate Stego Image", type="primary", use_container_width=True):
            with st.spinner("🧠 Neural network encoding + AES-256 encrypting..."):
                try:
                    ci=Image.open(cover_f); si=Image.open(secret_f)
                    ct_t,st_t=preprocess(ci),preprocess(si)
                    with torch.no_grad(): stego_t=hiding_net(ct_t,st_t)
                    stego_img=postprocess(stego_t); stego_bytes=to_bytes(stego_img)
                    cr=ci.convert("RGB").resize((IMG_SIZE,IMG_SIZE))
                    pv=calc_psnr(cr,stego_img); sv=calc_ssim(np.array(cr),np.array(stego_img))
                    dr=detection_score(pv,sv)
                    enc=encrypt_image_bytes(stego_bytes, passphrase)
                    st.session_state.stego_result={
                        "cover":cr,"secret":si,"stego":stego_img,
                        "psnr":pv,"ssim":sv,"dr":dr,"receiver":None,
                        "bytes":stego_bytes,"enc":enc,"sent":False
                    }
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
    elif cover_f and secret_f and not pp_set:
        st.markdown("---")
        st.warning("⬆️ Set your passphrase above first, then the Generate button will appear.")

    # ── RESULTS + SEND ────────────────────────────────────────────────────
    if st.session_state.stego_result:
        r = st.session_state.stego_result
        sent = r.get("sent", False)

        if sent:
            st.markdown(f"""<div class="success-banner">
            ✅ Encrypted & sent to <b>{r['receiver']}</b>! Only they can decrypt it with the passphrase.</div>""",
            unsafe_allow_html=True)
        else:
            st.markdown("""<div class="success-banner">
            ✅ Stego image generated & encrypted! You can download it or send it to a user below.</div>""",
            unsafe_allow_html=True)

        st.markdown(f"""<div class="metric-row">
        <div class="metric-card"><div class="metric-val">{r['psnr']} dB</div><div class="metric-lbl">PSNR</div></div>
        <div class="metric-card"><div class="metric-val">{r['ssim']}</div><div class="metric-lbl">SSIM</div></div>
        <div class="metric-card"><div class="metric-val">{r['dr']}%</div><div class="metric-lbl">Detection Resistance</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#34d399">AES-256</div><div class="metric-lbl">Encryption</div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("#### Result Comparison")
        c1,c2,c3=st.columns(3)
        with c1: st.image(r["cover"],use_container_width=True); st.markdown('<div class="img-label">Original Cover</div>',unsafe_allow_html=True)
        with c2: st.image(r["stego"],use_container_width=True); st.markdown('<div class="img-label">🔐 Stego Image</div>',unsafe_allow_html=True)
        with c3: st.image(pixel_diff_heatmap(np.array(r["cover"]),np.array(r["stego"])),use_container_width=True); st.markdown('<div class="img-label">🔥 Pixel Diff Heatmap</div>',unsafe_allow_html=True)

        st.download_button("⬇️ Download Stego Image",data=r["bytes"],file_name="stego.png",mime="image/png")

        # ── STEP 3 (Optional): Send to a recipient ────────────────────────
        if not sent:
            st.markdown("---")
            st.markdown("#### 📨 Step 3 — Send to Recipient")
            st.markdown("""<div class="info-banner" style="margin-bottom:1rem">
            Search for a user by their <b>username</b> or <b>Stego-ID</b> to send the encrypted stego image directly to their inbox.
            </div>""", unsafe_allow_html=True)

            sc1, sc2 = st.columns([3, 1])
            with sc1:
                sq = st.text_input("🔍 Enter username or Stego-ID", placeholder="e.g. Ram or DSS-7X4K2M", key="srch", label_visibility="collapsed")
            with sc2:
                search_btn = st.button("🔍 Search", use_container_width=True, key="search_btn")

            chosen = None
            if (sq and len(sq) >= 1) and search_btn:
                with st.spinner("Searching users..."):
                    st.session_state["_search_results"] = search_users(sq, uid)

            search_results = st.session_state.get("_search_results", [])
            if search_results:
                for u in search_results:
                    rc1, rc2 = st.columns([4, 1])
                    with rc1:
                        st.markdown(f"""<div class="glass-card" style="padding:12px 16px;margin-bottom:8px">
                        <div style="display:flex;align-items:center;gap:12px">
                        <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,#7c3aed,#2563eb);
                        display:flex;align-items:center;justify-content:center;font-size:1rem">👤</div>
                        <div>
                        <div style="font-weight:600;color:white;font-size:.92rem">{u['username']}</div>
                        <div style="font-size:.72rem;color:rgba(255,255,255,0.35);
                        font-family:'JetBrains Mono',monospace">{u['stego_id']}</div>
                        </div></div></div>""", unsafe_allow_html=True)
                    with rc2:
                        if st.button(f"📨 Send", key=f"send_{u['id']}", use_container_width=True):
                            chosen = u

                if chosen is None:
                    # Check if any send button was pressed
                    for u in search_results:
                        if st.session_state.get(f"send_{u['id']}"):
                            chosen = u
                            break
            elif sq and search_btn:
                st.markdown("""<div class="info-banner">
                😕 No users found. Double-check the username or Stego-ID.
                </div>""", unsafe_allow_html=True)

            note = st.text_input("📝 Note (optional)", placeholder="e.g. Check this out!", key="note")

            if chosen:
                with st.spinner(f"Uploading & sending to {chosen['username']}..."):
                    try:
                        enc = r["enc"]
                        fn = f"{uid}/{uuid.uuid4().hex}.enc"
                        upload_stego(enc["ct"], fn)
                        insert_message(uid, chosen["id"], fn, note, True, enc["nonce"], enc["salt"])
                        st.session_state.stego_result["receiver"] = chosen["username"]
                        st.session_state.stego_result["sent"] = True
                        if "_search_results" in st.session_state: del st.session_state["_search_results"]
                        st.rerun()
                    except Exception as e: st.error(f"Error sending: {e}")

        if st.button("🔄 Start New Encoding"):
            st.session_state.stego_result=None
            st.session_state["_passphrase_confirmed"]=False
            st.session_state["_passphrase_value"]=""
            if "_search_results" in st.session_state: del st.session_state["_search_results"]
            st.rerun()

# ═══════════════════ INBOX ═══════════════════
with tab_inbox:
    ch,cr=st.columns([4,1])
    with ch:
        st.markdown("""<div class="section-header">
        <span class="icon">📥</span><h2>Secret Inbox</h2></div>""", unsafe_allow_html=True)
    with cr:
        if st.button("🔄 Refresh",use_container_width=True,key="ref_in"): st.rerun()

    inbox=get_inbox(uid)
    if not inbox:
        st.markdown(f"""<div class="glass-card" style="text-align:center;padding:3rem">
        <div style="font-size:3rem;margin-bottom:1rem">📭</div>
        <div style="color:rgba(255,255,255,0.4);font-size:1rem">Your inbox is empty.<br>
        <span style="font-size:.85rem">Share your Stego-ID <b style="color:#a78bfa">{stego_id}</b> so others can send you images.</span>
        </div></div>""", unsafe_allow_html=True)
    else:
        unread=sum(1 for m in inbox if not m["revealed"])
        st.markdown(f"""<div class="metric-row">
        <div class="metric-card"><div class="metric-val">{len(inbox)}</div><div class="metric-lbl">Total</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#a78bfa">{unread}</div><div class="metric-lbl">Unrevealed</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#34d399">{len(inbox)-unread}</div><div class="metric-lbl">Revealed</div></div>
        </div>""", unsafe_allow_html=True)

        for msg in inbox:
            si=msg.get("profiles") or {}; sn=si.get("username","Unknown"); ssid=si.get("stego_id","")
            ir=msg["revealed"]; d=msg["created_at"][:10]
            cc="read" if ir else "unread"; sc="status-read" if ir else "status-unread"
            st_=("✅ Revealed" if ir else "🔒 Waiting")
            nh=f'<div style="color:rgba(255,255,255,0.4);font-size:.83rem;margin-top:6px">💬 {msg["note"]}</div>' if msg.get("note") else ""
            st.markdown(f"""<div class="msg-card {cc}"><div class="msg-meta">
            <span class="sender-tag">📨 From {sn}</span>
            <span style="color:rgba(255,255,255,0.25);font-family:'JetBrains Mono';font-size:.72rem">{ssid}</span>
            <span class="date-tag">{d}</span><span class="status-tag {sc}">{st_}</span>
            <span class="lock-tag">🔑 Passphrase</span>
            </div>{nh}</div>""", unsafe_allow_html=True)

            if not ir:
                pp_in=st.text_input("🔑 Enter passphrase to decrypt",type="password",key=f"pp_{msg['id']}")
                if st.button("🔓 Decrypt & Reveal",key=f"btn_{msg['id']}",use_container_width=True):
                    if not pp_in:
                        st.error("Passphrase required to decrypt.")
                    else:
                        with st.spinner("Decrypting & revealing..."):
                            try:
                                nonce=msg.get("encryption_iv",""); salt=msg.get("sender_public_key","")
                                enc=download_stego(msg["stego_path"])
                                dec=decrypt_image_bytes(enc, pp_in, nonce, salt)
                                stego_img=Image.open(io.BytesIO(dec)); stego_t=preprocess(stego_img)
                                with torch.no_grad(): rev_t=reveal_net(stego_t)
                                rev_img=postprocess(rev_t)
                                st.markdown(f"""<div class="success-banner">🎉 Secret revealed from <b>{sn}</b>!</div>""",unsafe_allow_html=True)
                                c1,c2=st.columns(2)
                                with c1: st.image(stego_img,use_container_width=True); st.markdown('<div class="img-label">🔒 Stego</div>',unsafe_allow_html=True)
                                with c2: st.image(rev_img,use_container_width=True); st.markdown('<div class="img-label">🤫 Revealed</div>',unsafe_allow_html=True)
                                st.download_button("⬇️ Download",data=to_bytes(rev_img),file_name=f"secret_{sn}.png",mime="image/png",key=f"dl_{msg['id']}")
                                mark_revealed(msg["id"])
                            except Exception as e:
                                if "tag" in str(e).lower() or "InvalidTag" in str(type(e).__name__):
                                    st.markdown('<div class="error-banner">❌ Wrong passphrase! Cannot decrypt.</div>',unsafe_allow_html=True)
                                else: st.error(f"Error: {e}")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ═══════════════════ DECODE (Upload) ═══════════════════
with tab_decode:
    st.markdown("""<div class="section-header">
    <span class="icon">🔓</span><h2>Decode Stego Image</h2></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="info-banner">
    Upload a stego image to reveal the hidden secret inside. If the image was <b>encrypted</b> with a passphrase,
    enter it below. If it's an <b>unencrypted</b> stego PNG (downloaded directly), just upload and reveal.
    </div>""", unsafe_allow_html=True)

    # Upload stego image
    st.markdown("#### 📤 Step 1 — Upload Stego Image")
    decode_file = st.file_uploader("Upload stego image", type=["jpg","jpeg","png"], key="decode_upload", label_visibility="collapsed")

    if decode_file:
        st.image(decode_file, use_container_width=True, caption="Uploaded Stego Image")

        # Optional passphrase
        st.markdown("#### 🔑 Step 2 — Passphrase (optional)")
        decode_pp = st.text_input("🔑 Passphrase", type="password", key="decode_pp",
                                   placeholder="Only needed if the image was encrypted with a passphrase...")
        st.markdown("""<div class="info-banner" style="font-size:.82rem">
        💡 If you <b>downloaded</b> the stego image directly, no passphrase is needed — just click Reveal.<br>
        If the image was <b>sent via the app</b>, use the <b>Inbox</b> tab instead for automatic decryption.
        </div>""", unsafe_allow_html=True)

        # Reveal button
        st.markdown("#### 🧠 Step 3 — Reveal Hidden Image")
        if st.button("🔓 Reveal Secret Image", type="primary", use_container_width=True, key="decode_reveal_btn"):
            with st.spinner("🧠 Running neural network reveal..."):
                try:
                    raw_bytes = decode_file.getvalue()

                    stego_img = Image.open(io.BytesIO(raw_bytes))
                    stego_t = preprocess(stego_img)
                    with torch.no_grad():
                        rev_t = reveal_net(stego_t)
                    rev_img = postprocess(rev_t)

                    st.markdown("""<div class="success-banner">🎉 Secret image revealed!</div>""",
                                unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.image(stego_img, use_container_width=True)
                        st.markdown('<div class="img-label">🔒 Stego Input</div>', unsafe_allow_html=True)
                    with c2:
                        st.image(rev_img, use_container_width=True)
                        st.markdown('<div class="img-label">🤫 Revealed Secret</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Download Revealed Image", data=to_bytes(rev_img),
                                       file_name="revealed_secret.png", mime="image/png", key="decode_dl")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════ SENT ═══════════════════
with tab_sent:
    st.markdown("""<div class="section-header">
    <span class="icon">📨</span><h2>Sent Messages</h2></div>""", unsafe_allow_html=True)
    sent=get_sent(uid)
    if not sent:
        st.markdown("""<div class="glass-card" style="text-align:center;padding:3rem">
        <div style="font-size:3rem;margin-bottom:1rem">📤</div>
        <div style="color:rgba(255,255,255,0.4)">No messages sent yet.</div></div>""",unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="metric-row">
        <div class="metric-card"><div class="metric-val">{len(sent)}</div><div class="metric-lbl">Total Sent</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#34d399">{sum(1 for m in sent if m['revealed'])}</div><div class="metric-lbl">Opened</div></div>
        <div class="metric-card"><div class="metric-val" style="color:#a78bfa">{sum(1 for m in sent if not m['revealed'])}</div><div class="metric-lbl">Pending</div></div>
        </div>""", unsafe_allow_html=True)
        for msg in sent:
            ri=msg.get("profiles") or {}; rn=ri.get("username","Unknown"); rsid=ri.get("stego_id","")
            d=msg["created_at"][:10]; op=msg["revealed"]
            st_=("✅ Opened" if op else "⏳ Pending"); sc=("status-read" if op else "status-unread")
            nh=f'<div style="color:rgba(255,255,255,0.4);font-size:.83rem;margin-top:6px">💬 {msg["note"]}</div>' if msg.get("note") else ""
            st.markdown(f"""<div class="msg-card"><div class="msg-meta">
            <span class="sender-tag">📨 To {rn}</span>
            <span style="color:rgba(255,255,255,0.25);font-family:'JetBrains Mono';font-size:.72rem">{rsid}</span>
            <span class="date-tag">{d}</span><span class="status-tag {sc}">{st_}</span>
            <span class="lock-tag">🔑</span>
            </div>{nh}</div>""", unsafe_allow_html=True)

# ═══════════════════ PROFILE ═══════════════════
with tab_profile:
    st.markdown("""<div class="section-header">
    <span class="icon">👤</span><h2>Profile & Security</h2></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="profile-id">
    <div class="id-lbl">YOUR STEGO-ID</div>
    <div class="id-val">{stego_id}</div>
    <div class="id-lbl" style="margin-top:8px">Share this so others can send you encrypted images</div>
    </div>""", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f"""<div class="glass-card">
        <div style="color:rgba(255,255,255,0.6);font-weight:700;margin-bottom:10px">📋 Account</div>
        <div style="color:rgba(255,255,255,0.5);font-size:.9rem;line-height:2">
        <b style="color:rgba(255,255,255,0.7)">Username:</b> {uname}<br>
        <b style="color:rgba(255,255,255,0.7)">Stego-ID:</b> <code>{stego_id}</code><br>
        <b style="color:rgba(255,255,255,0.7)">User ID:</b> <code>{uid[:12]}...</code>
        </div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="glass-card">
        <div style="color:rgba(255,255,255,0.6);font-weight:700;margin-bottom:10px">🔐 Security</div>
        <div style="color:rgba(255,255,255,0.5);font-size:.9rem;line-height:2">
        <b style="color:rgba(255,255,255,0.7)">Encryption:</b> AES-256-GCM<br>
        <b style="color:rgba(255,255,255,0.7)">Key Derivation:</b> PBKDF2-SHA256<br>
        <b style="color:rgba(255,255,255,0.7)">Protection:</b> Per-message passphrase
        </div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="info-banner">
    🛡️ <b>How it works:</b> When you send an image, you set a secret passphrase. The stego image is encrypted
    with AES-256-GCM using a key derived from your passphrase (PBKDF2, 480K iterations). The receiver must enter
    the exact same passphrase to decrypt. Without it, the encrypted file is unreadable — even by us.
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""<div style="text-align:center;color:rgba(255,255,255,0.15);font-size:.78rem;padding:1rem 0;
font-family:'Inter',sans-serif;letter-spacing:.02em">
Deep-Stego Secure · Dual U-Net · AES-256-GCM · PBKDF2 · PyTorch + Streamlit + Supabase
</div>""", unsafe_allow_html=True)