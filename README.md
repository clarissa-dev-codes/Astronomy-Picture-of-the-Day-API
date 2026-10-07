# 🌌 Astronomy Picture of the Day (APOD) - Windows Lock Screen App

A responsive, automated web application that leverages NASA's public API to fetch and display the daily space image and educational description. The layout features an elegant design inspired by the **Microsoft Windows Lock Screen**, utilizing a modern blur-effect data window tucked into the corner of a fullscreen canvas.

## 🔗 Live Deployment
Experience the live application here: 
👉 [https://clarissa-dev-codes.github.io/Astronomy-Picture-of-the-Day-API/](https://clarissa-dev-codes.github.io/Astronomy-Picture-of-the-Day-API/)

---

## 🛠️ System Architecture & Automation

To convert my original local terminal application into a global static web page while protecting server privacy, I built a serverless pipeline:
1. **Python Engine (`apod.py`)**: Connects to NASA endpoints using browser headers, captures payload parameters (Title, HD Image URL, Description), and dynamically rewrites a clean frontend markup template into an optimized `index.html`.
2. **GitHub Actions Workflow**: A cloud-based automation script scheduled via a cron job to fire **every morning at 8:00 AM UTC**. 
3. **GitHub Pages Deployment**: Rather than tracking changing data on the `main` branch, the background pipeline compiles the code and pushes the build artifacts directly to an isolated `gh-pages` branch for safe, reliable delivery.

---

## 💡 What I Learned During This Project

Building this project taught me several critical concepts across backend logic, security engineering, and cloud operations:

* **API Token Security & Git Hygiene**: I learned why hardcoding private credentials inside client-side JavaScript is dangerous for static builds. By creating a `.env` local architecture and moving keys over to **GitHub Repository Secrets**, I successfully protected my `NASA_API` token from open public exposure.
* **Continuous Integration & Automation (CI/CD)**: Setting up GitHub Actions taught me how to configure cloud workflow machines, manage automated build schedules, and grant precise read/write bot permissions.
* **Dynamic Web Generation**: Instead of manually editing text files, I used Python file I/O operations (`with open()`) to dynamically inject server data strings straight into production-ready HTML/CSS structures.
* **Responsive Visual Styling & Glassmorphism**: I learned how to work with viewport layout dimensions (`100vw` / `100vh`) and modern backdrop filters (`backdrop-filter: blur()`) to mimic premium OS desktop elements across dynamic screen sizes.

---

## 🗂️ Project Directory Layout

```text
├── .github/workflows/
│   └── update_apod.yml   # Cloud automation and deployment instructions
├── .gitignore            # Security rules ensuring local .env stays private
├── README.md             # Project documentation (You are here!)
├── apod.py               # Main Python processing file
├── index.html            # Compiled layout (dynamically updated daily)
└── LICENSE               # Open-source licensing documentation
```

---
*Developed as part of my ongoing development portfolio. Driven by curiosity and a love for the stars.* 🚀
