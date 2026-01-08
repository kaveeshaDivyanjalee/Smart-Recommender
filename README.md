# 🛒 Smart Recommender System

A **production-ready recommendation system** built with **Streamlit**, using
collaborative filtering (SVD) on Amazon Electronics data.

🚀 Live App:  
👉 https://huggingface.co/spaces/kaveesha-divyanjalee/smart-recommender

---

## ✨ Features

- 🔐 User authentication (Login / Signup / Reset)
- 👑 Admin dashboard
- 👍👎 User feedback (Like / Dislike)
- 🧠 SVD-based collaborative filtering
- 📦 Auto-download datasets & model
- ☁️ Cloud-ready (Hugging Face / Streamlit)

---

## 🧠 Tech Stack

- Python
- Streamlit
- Pandas / NumPy
- Scikit-learn
- GitHub Releases (for large files)
- Hugging Face Spaces

---

## 📂 Project Structure

Smart-Recommender/
├── app.py
├── requirements.txt
├── README.md
├── data/ # auto-created
└── models/ # auto-created

---

## ⬇️ Dataset & Model Handling

Large files are **NOT stored in GitHub repo**.

They are downloaded automatically from **GitHub Releases** at runtime:

- Electronics.csv.gz
- asin_title_map.csv
- asin_image_map.csv
- final_svd_model.pkl

No manual setup needed ✅

---

## ▶️ Run Locally

```bash
git clone https://github.com/kaveeshaDivyanjalee/Smart-Recommender.git
cd Smart-Recommender
pip install -r requirements.txt
streamlit run app.py

👑 Admin Login
Username: admin
Password: admin123

🌐 Deployment
This app is deployed on Hugging Face Spaces using Gradio SDK (Streamlit-compatible).

👩‍💻 Author
Kaveesha Divyanjalee
🚀 Final Year Project | Recommendation Systems

🔗 GitHub: https://github.com/kaveeshaDivyanjalee
🔗 LinkedIn: https://www.linkedin.com/in/kaveesha-divyanjalee-2bb7a2313/
