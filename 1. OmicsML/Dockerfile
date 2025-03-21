FROM python:3.9

WORKDIR /app

# 安裝 Python 依賴與 Jupyter
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install jupyter ipykernel  # 安裝 Jupyter 與 Kernel 管理工具

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root"]
