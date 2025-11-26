import requests
import random
import time

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    # 1. Create Operators
    print("Создание операторов...")
    op1 = requests.post(f"{BASE_URL}/operators/", json={"name": "Op1", "load_limit": 50}).json()
    op2 = requests.post(f"{BASE_URL}/operators/", json={"name": "Op2", "load_limit": 50}).json()
    
    # 2. Create Source
    print("Создание источника...")
    source = requests.post(f"{BASE_URL}/sources/", json={"name": f"Bot_{random.randint(1000,9999)}"}).json()
    
    # 3. Allocations (1:3 ratio)
    print("Настройка весов...")
    requests.post(f"{BASE_URL}/sources/{source['id']}/allocations", json=[
        {"operator_id": op1['id'], "weight": 10},
        {"operator_id": op2['id'], "weight": 30}
    ])
    
    # 4. Simulate Interactions
    print("Симуляция 100 обращений...")
    op1_count = 0
    op2_count = 0
    none_count = 0
    
    for i in range(100):
        lead_id = f"user_{i}@example.com"
        resp = requests.post(f"{BASE_URL}/interactions/", json={
            "lead_identifier": lead_id,
            "source_id": source['id']
        })
        if resp.status_code != 200:
            print(f"Ошибка: {resp.text}")
            continue
            
        data = resp.json()
        if data['operator_id'] == op1['id']:
            op1_count += 1
        elif data['operator_id'] == op2['id']:
            op2_count += 1
        else:
            none_count += 1
            
    print(f"Результаты:")
    print(f"Op1 (Вес 10): {op1_count}")
    print(f"Op2 (Вес 30): {op2_count}")
    print(f"Не назначено: {none_count}")
    
    # Verify ratio roughly 1:3
    total = op1_count + op2_count
    if total > 0:
        ratio = op1_count / total
        print(f"Доля Op1: {ratio:.2f} (Ожидается ~0.25)")

if __name__ == "__main__":
    # Wait for server to start if running immediately
    try:
        run_test()
    except Exception as e:
        print(f"Тест провален: {e}")
        print("Убедитесь, что uvicorn запущен: uvicorn main:app --reload")
