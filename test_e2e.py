import httpx
import asyncio

async def test_e2e():
    base_url = "http://127.0.0.1:8000/api"
    # Una foto pública cualquiera de un canal o basura
    photo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Ganges_river_pollution.jpg/800px-Ganges_river_pollution.jpg"
    
    print("1. Creando reporte inicial...")
    async with httpx.AsyncClient() as client:
        # 1. Crear reporte
        create_res = await client.post(
            f"{base_url}/reports",
            json={"photo_url": photo_url}
        )
        report = create_res.json()
        print(f"Reporte creado: {report}")
        report_id = report["id"]
        
        print("\n2. Mandando a analizar por Gemini (Fase 4)... esto puede tomar un par de segundos...")
        # 2. Analizar
        analyze_res = await client.post(
            f"{base_url}/ai/analizar",
            json={"report_id": report_id},
            timeout=30.0
        )
        ai_result = analyze_res.json()
        print(f"Análisis IA: {ai_result}")

if __name__ == "__main__":
    asyncio.run(test_e2e())
