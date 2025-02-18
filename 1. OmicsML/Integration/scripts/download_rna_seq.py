#!/usr/bin/env python3

import os
import requests
import pandas as pd
from tqdm import tqdm
import argparse
from pathlib import Path

def download_file(file_id: str, file_name: str, output_path: Path, gdc_api_url: str) -> bool:
    """
    Download a single file from GDC API
    
    Parameters:
    -----------
    file_id : str
        GDC file ID
    file_name : str
        Name of the file to save
    output_path : Path
        Path to save the downloaded file
    gdc_api_url : str
        GDC API endpoint template
        
    Returns:
    --------
    bool
        True if download successful, False otherwise
    """
    try:
        data_endpt = gdc_api_url.format(file_id)
        response = requests.get(
            data_endpt, 
            headers={"Content-Type": "application/json"}, 
            stream=True
        )

        if response.status_code == 200:
            total_size = int(response.headers.get("Content-Length", 0))
            block_size = 1024  # 1KB chunks

            with open(output_path / file_name, "wb") as output_file, tqdm.wrapattr(
                output_file, "write", total=total_size, desc=file_name, disable=True
            ) as wrapped_file:
                for chunk in response.iter_content(block_size):
                    wrapped_file.write(chunk)

            tqdm.write(f"✅ Downloaded successfully: {file_name}")
            return True
        else:
            tqdm.write(f"❌ Download failed for {file_name}, Status Code: {response.status_code}")
            return False
            
    except Exception as e:
        tqdm.write(f"❌ Error downloading {file_name}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download RNA-seq files from GDC API')
    parser.add_argument('--case-file', type=str, required=True,
                      help='Path to CSV file containing case and file information')
    parser.add_argument('--output-dir', type=str, required=True,
                      help='Directory to store downloaded files')
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # GDC API endpoint
    gdc_api_url = "https://api.gdc.cancer.gov/data/{}"
    
    # Load case to file mapping
    case_to_file_df = pd.read_csv(args.case_file)
    
    # Initialize progress bar
    with tqdm(total=len(case_to_file_df), desc="📥 Download Progress", unit="file") as progress_bar:
        for _, row in case_to_file_df.iterrows():
            file_id, file_name = row["File ID"], row["File Name"]
            file_path = output_path / file_name
            
            # Check if file already exists
            if file_path.exists():
                tqdm.write(f"✅ {file_name} already exists. Skipping download.")
                progress_bar.update(1)
                continue
                
            # Download file
            success = download_file(file_id, file_name, output_path, gdc_api_url)
            progress_bar.update(1)
    
    print("\n🎯 All files have been processed successfully!")

if __name__ == "__main__":
    main() 