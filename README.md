# 🔐 Deep-Stego Secure

**Military-grade neural image steganography with AES-256 encryption.**
Hide sensitive information inside images — invisible, secure, and intelligent.

---

## 🚀 Live Demo

👉 **Run the project here:**
https://huggingface.co/spaces/PradhyumnJ/deep-stego-secure

---

## 🧠 Project Overview

Deep-Stego Secure combines **deep learning + cryptography** to securely embed hidden messages inside images.

### 🔄 Workflow

1. User enters secret message
2. Message is encrypted using **AES-256-GCM**
3. Encrypted data is embedded into an image using **Dual U-Net**
4. Output: Stego image (visually unchanged)
5. Receiver uploads image → decrypts using passphrase

---

## ✨ Features

* 🔐 **AES-256-GCM Encryption** (passphrase-based)
* 🧠 **Dual U-Net Neural Architecture**
* 🖼️ **Image-based Steganography**
* 🔄 **Encode + Decode pipeline**
* ☁️ **Live deployment on Hugging Face**
* 📡 **Secure message transfer via images**

---

## 🏗️ Tech Stack

* **PyTorch** – Deep learning models
* **Streamlit** – Web interface
* **Supabase** – Backend (Auth, DB, Storage)
* **Cryptography** – AES-256-GCM + PBKDF2

---

## 📦 Model Weights

Model files are hosted on Hugging Face (not included in repo):

* `best.pt` → (add link)
* `best_slim.pt` → (add link)

---

## ⚙️ Local Setup

```bash
git clone https://github.com/PradhyumnJadhao/deep-stego-secure
cd deep-stego-secure

pip install -r requirements.txt
```

### ▶️ Run App

```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
deep-stego-secure/
│
├── app.py
├── crypto_utils.py
├── requirements.txt
├── README.md
├── deep-stego.ipynb (optional)
```

---

## ⚠️ Notes

* Model weights are excluded to keep repo lightweight
* Download models from Hugging Face before running locally
* Ensure correct paths in `app.py`

---

## 🎯 Use Cases

* Secure communication
* Digital watermarking
* Covert data transmission
* Privacy-focused messaging

---