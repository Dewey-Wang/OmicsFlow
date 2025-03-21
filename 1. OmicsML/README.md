# 📌 OmicsML:
*Integrating Transcriptomics & Proteomics for Cancer Subtyping and Identify key biomarkers*  

## **Overview**  
OmicsML is an **multi-omics analysis workflow** that integrates **RNA-Seq (Transcriptomics), Proteomics, mutation, and clinical data** to:  

✅ **Classify cancer subtypes**  
✅ **Identify key biomarkers**  

---

### **RNA-Seq Data (Transcriptomics)**  
**Source:** [GDC Data Portal](https://portal.gdc.cancer.gov/)  

- **Program:** CPTAC  
- **Project:** CPTAC-2  
- **Experimental Strategy:** **RNA-Seq**  
- **Workflow Type:** **STAR - Counts**  
- **Data Type:** **Gene Expression Quantification**  
- **Primary Site:** **Breast**  
- **Tissue Types:**  
  - **Primary Tumor** (Cancer Samples)  
- **Tumor Descriptor:** **Primary**  
- **Platform:** **Illumina**  
- **Data Format:** **TSV**  
- **Access:** **Open**

### **Mutation dataset**
**Source:** [cBioPortal](https://www.cbioportal.org/study/summary?id=brca_tcga_gdc)

### **Proteomics Data**  
**Source:** [Proteomic Data Commons (PDC)](https://pdc.cancer.gov/)  

- **Primary Site:** **Breast**  
- **Disease Type:** **Breast Invasive Carcinoma**  
- **Sample Type:** **Primary Tumor**  
- **Data Category:** **Protein Assembly**  
- **Access:** **Open**  
- **Studies Selected:**  
  - **Prospective Breast BI Proteome**  

📌 **Additional Normal Tissue Control:**  
- **GTEx Normal Tissue Transcriptomics** from the [GTEx Portal](https://gtexportal.org/)  

---

## **Project Workflow**  

### **📥 Phase 1: Data Collection & Preprocessing**  
- **Download RNA-Seq & Proteomics data** from TCGA, PDC, and GTEx.  
- **Normalize & preprocess omics data** (batch correction, missing value imputation).  
- **Use PCA & UMAP for dimensionality reduction**.  

### **📊 Phase 2: Feature Engineering & Multi-Omics Integration **  
- **Identify key biomarkers** using **Lasso regression, SHAP, and statistical tests**.  
- **Integrate multi-omics data** using **WGCNA (Weighted Gene Co-Expression Network Analysis)** & **Canonical Correlation Analysis (CCA)**.  
- **Extract highly correlated transcriptomic & proteomic features** for predictive modeling.  

---

## **4️⃣ Data Sources**  
| **Dataset** | **Omics Type** | **Source** |  
|------------|--------------|------------|  
| **Genomic Data Commons** | RNA-Seq (STAR-Counts), Clinical | [GDC](https://portal.gdc.cancer.gov/) |  
| **Proteomic Data Commons** | Proteomics | [PDC](https://pdc.cancer.gov/) |  
| **cBioPortal** | mutation | [cBioPortal]([https://pdc.cancer.gov/](https://www.cbioportal.org/study/summary?id=brca_tcga_gdc)) |  
| **GTEx** | Normal Tissue Transcriptomics | [GTEx Portal](https://gtexportal.org/) |  

---

## **📩 Contact & Collaboration**  
📧 Email: [deweywang2000@gmail.com](mailto:deweywang2000@gmail.com)  
🔗 LinkedIn: [linkedin.com/in/deweywang](https://linkedin.com/in/deweywang)  

🚀 *Let's push the boundaries of AI-driven multi-omics analysis together!*  
