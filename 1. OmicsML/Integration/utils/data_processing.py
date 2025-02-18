import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict
import os

def ensure_directory(directory: str) -> None:
    """
    Create directory if it doesn't exist
    
    Parameters:
    -----------
    directory : str
        Path to the directory to be created
        Format: "path/to/directory"
    
    Returns:
    --------
    None
    """
    os.makedirs(directory, exist_ok=True)

def load_and_clean_dataframe(file_path: str, sep: str = "\t", index_col: str = None) -> pd.DataFrame:
    """
    Load and perform basic cleaning of a dataframe
    
    Parameters:
    -----------
    file_path : str
        Path to the input file
        Format: "path/to/file.tsv" or "path/to/file.csv"
    sep : str, default="\t"
        Delimiter to use for file reading
        Format: "\t" for TSV, "," for CSV
    index_col : str, optional
        Name of column to set as index
        Format: Column name as string
    
    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe
        Format: Pandas DataFrame with specified index if provided
    """
    df = pd.read_csv(file_path, sep=sep, low_memory=False)
    if index_col:
        df = df.set_index(index_col)
    return df

def find_matched_samples(gdc_df: pd.DataFrame, pdc_df: pd.DataFrame) -> Tuple[set, set, set]:
    """
    Find matched samples between RNA-Seq and proteomics data
    
    Parameters:
    -----------
    gdc_df : pandas.DataFrame
        GDC RNA-Seq sample information
        Format: Must contain "Case ID" column
    pdc_df : pandas.DataFrame
        PDC proteomics sample information
        Format: Must contain "Case Submitter ID" column
    
    Returns:
    --------
    Tuple[set, set, set]
        Three sets containing:
        1. matched_samples: Samples present in both datasets
        2. proteomics_only: Samples unique to proteomics
        3. rna_seq_only: Samples unique to RNA-Seq
        Format: ({"id1", "id2"}, {"id3"}, {"id4"})
    """
    gdc_samples = set(gdc_df["Case ID"].astype(str))
    pdc_samples = set(pdc_df["Case Submitter ID"].astype(str))
    
    matched_samples = pdc_samples.intersection(gdc_samples)
    proteomics_only = pdc_samples - gdc_samples
    rna_seq_only = gdc_samples - pdc_samples
    
    return matched_samples, proteomics_only, rna_seq_only

def process_proteomics_data(proteomic_df: pd.DataFrame, 
                          matched_df: pd.DataFrame,
                          metadata_df: pd.DataFrame,
                          output_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Process proteomics data and separate into log ratio and unshared log ratio data
    
    Parameters:
    -----------
    proteomic_df : pandas.DataFrame
        Raw proteomics data
        Format: Must contain "Gene" column and sample columns with "Log Ratio" in names
    matched_df : pandas.DataFrame
        Matched sample information
        Format: Must contain "Aliquot Submitter ID" column
    metadata_df : pandas.DataFrame
        Sample metadata
        Format: Must contain "AnalyticalSample" column and aliquot columns
    output_dir : str
        Directory to save output files
        Format: "path/to/output/directory"
    
    Returns:
    --------
    Tuple[pd.DataFrame, pd.DataFrame]
        Two dataframes containing:
        1. log_df: Log ratio data
        2. unshared_df: Unshared log ratio data
        Format: Both with genes as index and samples as columns
    """
    # Get list of matched sample IDs
    aliquot_ids = matched_df["Aliquot Submitter ID"].tolist()
    
    # Get all column names
    proteomic_cols = proteomic_df.columns
    
    # Separate Log Ratio and Unshared Log Ratio columns
    log_ratio_cols = [col for col in proteomic_cols 
                     if any(aliquot in col for aliquot in aliquot_ids) 
                     and "Log Ratio" in col 
                     and "Unshared" not in col]
    
    unshared_log_ratio_cols = [col for col in proteomic_cols 
                              if any(aliquot in col for aliquot in aliquot_ids) 
                              and "Unshared Log Ratio" in col]
    
    # Create column name mapping (only keep aliquot ID)
    log_ratio_cleaned = {col: col.split()[0] for col in log_ratio_cols}
    unshared_log_ratio_cleaned = {col: col.split()[0] for col in unshared_log_ratio_cols}
    
    # Extract and rename data
    log_df = proteomic_df[["Gene"] + log_ratio_cols].rename(columns=log_ratio_cleaned)
    unshared_df = proteomic_df[["Gene"] + unshared_log_ratio_cols].rename(columns=unshared_log_ratio_cleaned)
    
    # Set Gene as index
    log_df.set_index("Gene", inplace=True)
    unshared_df.set_index("Gene", inplace=True)
    
    # Create mapping from Aliquot ID to Analytical Sample
    aliquot_to_sample = {}
    for _, row in metadata_df.iterrows():
        analytical_sample = row["AnalyticalSample"]
        for col in row.index[2:]:  # Aliquot IDs start from the 3rd column
            if isinstance(row[col], str):  # Only keep valid Aliquot IDs
                aliquot_to_sample[row[col]] = analytical_sample
    
    # Add AnalyticalSample column
    log_df = log_df.T  # Transpose to make Aliquot IDs the index
    log_df["AnalyticalSample"] = log_df.index.map(aliquot_to_sample)
    log_df = log_df.T  # Transpose back
    
    unshared_df = unshared_df.T
    unshared_df["AnalyticalSample"] = unshared_df.index.map(aliquot_to_sample)
    unshared_df = unshared_df.T
    
    # Process duplicate samples
    duplicate_samples = matched_df[matched_df.duplicated(subset=["Case Submitter ID"], keep=False)]
    if not duplicate_samples.empty:
        duplic_ids = set(duplicate_samples["Aliquot Submitter ID"])
        pd.DataFrame({"Aliquot Submitter ID": list(duplic_ids)}).to_csv(
            f"{output_dir}/aliquot_ids_with_multiple_matches.csv", index=False
        )
    
    # Save processed data
    log_df.to_csv(f"{output_dir}/log_transformed_data.csv")
    unshared_df.to_csv(f"{output_dir}/unshared_data.csv")
    
    return log_df, unshared_df

def perform_zscore_normalization(data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform Z-score normalization using StandardScaler
    
    Parameters:
    -----------
    data_df : pandas.DataFrame
        Input dataframe to be normalized
        Format: Numeric values only, no missing values
        
    Returns:
    --------
    pd.DataFrame
        Normalized dataframe
        Format: Same dimensions as input, values normalized to mean=0, std=1
    """
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(data_df)
    
    return pd.DataFrame(
        normalized_data,
        index=data_df.index,
        columns=data_df.columns
    )

def perform_pca_analysis(data_df: pd.DataFrame, title: str, perform_zscore: bool = True) -> pd.DataFrame:
    """
    Perform PCA analysis and visualize results
    
    Parameters:
    -----------
    data_df : pandas.DataFrame
        Gene expression data
        Format: rows = genes + 'AnalyticalSample' row, columns = sample IDs
        Required rows: 'AnalyticalSample', 'Mean', 'Median', 'StdDev'
    title : str
        Plot title
        Format: String to be displayed as plot title
    perform_zscore : bool, default=True
        Whether to perform Z-score normalization
        Format: True/False
    
    Returns:
    --------
    pd.DataFrame
        PCA results
        Format: Columns = ['PC1', 'PC2', 'AnalyticalSample'], rows = samples
    """
    # Extract AnalyticalSample and remove statistical rows
    analytical_samples = data_df.loc['AnalyticalSample'].copy()
    data_for_pca = data_df.drop('AnalyticalSample')
    
    # Fill NaN with Mean values
    data_for_pca = data_for_pca.fillna(data_for_pca.loc['Mean'])
    
    # Remove statistical rows
    data_for_pca = data_for_pca.drop(['Mean', 'Median', 'StdDev'])
    
    # Transpose for PCA
    data_for_pca = data_for_pca.T
    
    # Optional Z-score normalization
    if perform_zscore:
        data_for_pca = perform_zscore_normalization(data_for_pca)
    
    # Perform PCA
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(data_for_pca)
    
    # Create results DataFrame
    pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
    pca_df['AnalyticalSample'] = analytical_samples.reset_index(drop=True)
    
    # Plot
    plt.figure(figsize=(10, 7))
    sns.scatterplot(data=pca_df, x='PC1', y='PC2', 
                    hue='AnalyticalSample', palette='tab10', alpha=0.8)
    
    # Add Z-score info to title
    z_score_info = "with Z-score" if perform_zscore else "without Z-score"
    full_title = f"{title}\n({z_score_info})"
    
    # Set plot attributes
    plt.title(full_title)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.2f}%)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.2f}%)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return pca_df

def merge_duplicate_samples(df: pd.DataFrame, duplic_ids: set) -> pd.DataFrame:
    """
    Merge duplicate samples by taking their mean values
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input dataframe with genes as index and samples as columns
        Format: rows = genes, columns = sample IDs
    duplic_ids : set
        Set of duplicate sample IDs to be merged
        Format: {'sample_id1', 'sample_id2', ...}
        
    Returns:
    --------
    pd.DataFrame
        Merged dataframe with averaged values for duplicate samples
        Format: Same as input, but with merged duplicate columns
    """
    # Remove statistical summary rows
    df_no_duplicates = df.drop(index=["Mean", "Median", "StdDev", "AnalyticalSample"], errors="ignore")
    
    # Convert to float type
    df_no_duplicates = df_no_duplicates.apply(pd.to_numeric, errors="coerce")
    
    # Create mapping for duplicate IDs
    mapping = {}
    for sample_id in df_no_duplicates.columns:
        for dup_id in duplic_ids:
            if sample_id.startswith(dup_id):
                mapping[sample_id] = dup_id
    
    # Rename and merge
    df_no_duplicates = df_no_duplicates.rename(columns=mapping)
    df_merged = df_no_duplicates.T.groupby(level=0).mean().T
    
    return df_merged

def plot_expression_boxplot(data_df: pd.DataFrame, title: str, perform_zscore: bool = True) -> None:
    """
    Plot boxplot of gene expression distribution
    
    Parameters:
    -----------
    data_df : pandas.DataFrame
        Gene expression data with AnalyticalSample row
        Format: rows = genes + metadata rows, columns = sample IDs
        Required rows: 'AnalyticalSample', 'Mean', 'Median', 'StdDev'
    title : str
        Plot title
        Format: String to be displayed as plot title
    perform_zscore : bool, default=True
        Whether to perform Z-score normalization
        Format: True/False
        
    Returns:
    --------
    None
        Displays a boxplot visualization
    """
    # Prepare data
    melted_df = data_df.copy()
    analytical_samples = melted_df.loc['AnalyticalSample']
    
    # Remove statistical rows and transpose
    data_for_plot = melted_df.drop(['AnalyticalSample', 'Mean', 'Median', 'StdDev']).T
    
    # Optional Z-score normalization
    if perform_zscore:
        data_for_plot = perform_zscore_normalization(data_for_plot)
    
    # Add AnalyticalSample information
    data_for_plot['AnalyticalSample'] = analytical_samples
    
    # Convert to long format
    melted_df = data_for_plot.melt(
        id_vars=['AnalyticalSample'], 
        var_name='Gene', 
        value_name='Expression'
    )
    
    # Plot
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='AnalyticalSample', y='Expression', data=melted_df)
    
    # Add Z-score info to title
    z_score_info = "with Z-score" if perform_zscore else "without Z-score"
    full_title = f"{title}\n({z_score_info})"
    
    # Set plot attributes
    plt.xticks(rotation=90)
    plt.title(full_title)
    plt.xlabel('AnalyticalSample (Batch)')
    plt.ylabel('Expression Level')
    
    plt.tight_layout()
    plt.show()

def create_case_to_file_mapping(matched_samples_path: str, 
                              gdc_sample_sheet_path: str, 
                              output_dir: str = None) -> pd.DataFrame:
    """
    Create and optionally save a mapping between case IDs and their corresponding file information
    
    Parameters:
    -----------
    matched_samples_path : str
        Path to CSV file containing matched samples information
        Format: Must contain "Case Submitter ID" column
        Example: "dataset/processed/1. Data_preparation-matching_ID/Proteome/matched_samples_with_aliquot.csv"
    gdc_sample_sheet_path : str
        Path to GDC sample sheet TSV file
        Format: Must contain "Case ID", "File ID", and "File Name" columns
        Example: "dataset/CPTAC/RNA-Seq/gdc_sample_sheet.2025-02-14.tsv"
    output_dir : str, optional
        Directory to save the mapping file
        Format: "path/to/output/directory"
        If provided, will save the mapping to "rna_seq_file_mapping.csv" in this directory
    
    Returns:
    --------
    pd.DataFrame
        DataFrame containing case-to-file mapping
        Format: Columns = ["Case ID", "File ID", "File Name"]
    """
    # Load the case-to-file mapping data
    matched_df = pd.read_csv(matched_samples_path)
    gdc_df = pd.read_csv(gdc_sample_sheet_path, sep="\t")

    # Ensure Case IDs are strings to prevent type mismatch
    matched_samples = set(matched_df["Case Submitter ID"].astype(str))

    # Create a mapping of Case ID → (File ID, File Name)
    case_to_file = {
        row["Case ID"]: (row["File ID"], row["File Name"])
        for _, row in gdc_df.iterrows() if row["Case ID"] in matched_samples
    }

    # Convert to DataFrame for easier visualization
    case_to_file_df = pd.DataFrame(
        [(case, file_id, file_name) for case, (file_id, file_name) in case_to_file.items()],
        columns=["Case ID", "File ID", "File Name"]
    )
    
    # Save the mapping if output_dir is provided
    if output_dir:
        ensure_directory(output_dir)
        output_path = os.path.join(output_dir, "rna_seq_file_mapping.csv")
        case_to_file_df.to_csv(output_path, index=False)
        print(f"✅ RNA-seq file mapping has been saved to:")
        print(f"📂 {output_path}")
    
    return case_to_file_df