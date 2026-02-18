import os
import zipfile
import requests
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BCBDataExtractor:
    def __init__(self, year: int, base_download_dir: str = "data/raw"):
        self.year = year
        self.base_url = f"https://www.bcb.gov.br/pda/desig/planilha_{self.year}.zip"
        self.download_dir = Path(base_download_dir)
        self.zip_path = self.download_dir / f"scrdata_{self.year}.zip"
        
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def download_zip(self) -> bool:
        """Faz o download do arquivo ZIP do Banco Central."""
        logging.info(f"Iniciando download dos dados SCR referentes ao ano {self.year}...")
        try:
            response = requests.get(self.base_url, stream=True)
            response.raise_for_status()
            
            with open(self.zip_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            logging.info("Download concluído com sucesso.")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao baixar os dados do ano {self.year}: {e}")
            return False

    def extract_and_convert_to_parquet(self):
        """Extrai os CSVs do ZIP e os converte para Parquet."""
        if not self.zip_path.exists():
            logging.error("Arquivo ZIP não encontrado para extração.")
            return

        logging.info("Iniciando extração e conversão para Parquet...")
        
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            
            for csv_file in csv_files:
                zip_ref.extract(csv_file, path=self.download_dir)
                csv_path = self.download_dir / csv_file
                parquet_path = self.download_dir / csv_file.replace('.csv', '.parquet')
                
                try:
                    logging.info(f"Convertendo {csv_file} para Parquet...")
                    df = pd.read_csv(csv_path, sep=';', encoding='utf-8', low_memory=False)
                    
                    df.to_parquet(parquet_path, engine='pyarrow', index=False)
                    
                    os.remove(csv_path)
                    
                except Exception as e:
                    logging.error(f"Erro ao processar o arquivo {csv_file}: {e}")

        os.remove(self.zip_path)
        logging.info(f"Processamento do ano {self.year} finalizado. Arquivos salvos em {self.download_dir}")

if __name__ == "__main__":
    anos_alvo = [2024, 2025, 2026]
    
    for ano in anos_alvo:
        print(f"==================================================")
        print(f"🚀 Iniciando extração do SCR para o ano: {ano}")
        print(f"==================================================")
        
        extractor = BCBDataExtractor(year=ano)
        
        if extractor.download_zip():
            extractor.extract_and_convert_to_parquet()
            print(f"✅ Processamento do ano {ano} concluído com sucesso!\n")
        else:
            print(f"❌ Falha ao processar o ano {ano}. Pulando para o próximo...\n")
            
    print("🎉 Extração de todos os anos finalizada!")