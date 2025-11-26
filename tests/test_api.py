def test_create_operator(client):
    response = client.post(
        "/operators/",
        json={"name": "Test Operator", "load_limit": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Operator"
    assert data["id"] is not None

def test_read_operators(client):
    client.post("/operators/", json={"name": "Op1", "load_limit": 5})
    client.post("/operators/", json={"name": "Op2", "load_limit": 5})
    
    response = client.get("/operators/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_create_source(client):
    response = client.post(
        "/sources/",
        json={"name": "Test Source", "weight": 1.5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Source"
    # Source model does not have weight, it's in the link
    # assert data["weight"] == 1.5

def test_create_interaction(client):
    # Setup
    op_res = client.post("/operators/", json={"name": "Op1", "load_limit": 5})
    op_id = op_res.json()["id"]
    
    src_res = client.post("/sources/", json={"name": "Src1", "weight": 1.0})
    src_id = src_res.json()["id"]
    
    # Allocation
    client.post(f"/sources/{src_id}/allocations", json=[{"operator_id": op_id, "weight": 100}])
    
    # Create interaction
    response = client.post(
        "/interactions/",
        json={"source_id": src_id, "lead_identifier": "1234567890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operator_id"] == op_id
    assert data["status"] == "OPEN"
