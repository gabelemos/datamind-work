<h2>DataMind - Work 🧠☕</h2>
<h4>Esse projeto foi criado para apresentação na matéria
"Desenvolvimento Rápido de Aplicações em Python"</h4>

<p>Com a recente aprovação da NR-1, notamos que o ambiente de trabalho vem passando por muitas adaptações ao longo do tempo, curiosamente várias após a pandemia causada pelo COVID-19. Principalmente quando o assunto é saúde mental de colaboradores.</p>

<p>O projeto analisa dados públicos do SINAN/DataSUS — base <strong>MENTBR</strong> (Transtornos Mentais e Comportamentais Relacionados ao Trabalho) — comparando <strong>3 anos antes</strong> e <strong>4 anos depois</strong> da pandemia para evidenciar o impacto real no ambiente de trabalho.</p>

<hr>

| Stacks Utilizadas |
|----------|
| ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) |
| ![Pandas](https://img.shields.io/badge/Pandas-150458.svg?style=for-the-badge&logo=pandas&logoColor=white) |
| ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white) |
| ![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white) |
| ![Matplotlib](https://img.shields.io/badge/Matplotlib-f7f1f1?style=for-the-badge&logo=python&logoColor=black) |
| ![PyArrow](https://img.shields.io/badge/PyArrow-000000?style=for-the-badge&logo=apache&logoColor=white) |

<hr>

<h3>⚙️ Requisitos</h3>

- Python **3.11** (obrigatório — versões mais novas não são compatíveis com `pyreaddbc`)
- Windows: **Microsoft C++ Build Tools** instalado

<hr>

<h3>▶️ How-To-Run</h3>

**1. Clone o repositório**
```bash
git clone https://github.com/sergiobfj/datamind-work.git
cd datamind-work
```

**2. Crie a virtual environment com Python 3.11**
```bash
py -3.11 -m venv venv311
```

**3. Ative a venv**

Windows (PowerShell):
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& venv311\Scripts\Activate.ps1
```

**4. Instale as dependências**
```bash
pip install pyreaddbc pandas numpy streamlit plotly matplotlib pyarrow
```

**5. Rode o projeto**
```bash
streamlit run app.py
```

<hr>

<h3>📁 Estrutura</h3>