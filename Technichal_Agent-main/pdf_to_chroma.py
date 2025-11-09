# extract_havells_with_embeddings.py
import pdfplumber
import pandas as pd
import re
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib

# Initialize the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

pdf_path = "Catalogue_Havells_International_Cables.pdf"
outdir = Path("havells_parsed")
outdir.mkdir(exist_ok=True)

def clean_header(h):
    return re.sub(r'\s+', ' ', str(h)).strip()

def normalize_numeric(s):
    if s is None: return None
    s = str(s).strip()
    s = s.replace(',', '')
    m = re.search(r'[-+]?[0-9]*\.?[0-9]+', s)
    if m:
        try:
            return float(m.group(0))
        except:
            return None
    return None

def generate_record_id(record, meta):
    """Generate unique ID for each record"""
    content_str = f"{record.get('conductor_nominal_area_mm2', '')}_{meta['page']}_{meta['table_index']}"
    return hashlib.md5(content_str.encode()).hexdigest()

def create_record_embedding(record, meta):
    """Create embedding for a single cable record"""
    
    # Build descriptive text for embedding
    components = []
    
    # Basic cable description
    area = record.get('conductor_nominal_area_mm2')
    if area:
        components.append(f"{area} sq mm cable")
    
    # Technical specifications
    specs = []
    if record.get('current_rating_amps'):
        specs.append(f"{record['current_rating_amps']} amps current rating")
    if record.get('approx_overall_diameter_mm'):
        specs.append(f"{record['approx_overall_diameter_mm']} mm diameter")
    if record.get('overall_weight_kg_per_km'):
        specs.append(f"{record['overall_weight_kg_per_km']} kg/km weight")
    
    if specs:
        components.append("with " + ", ".join(specs))
    
    # Construction details
    construction = []
    if record.get('insulation_thickness_mm'):
        construction.append(f"{record['insulation_thickness_mm']} mm insulation")
    if record.get('outer_sheath_thickness_mm'):
        construction.append(f"{record['outer_sheath_thickness_mm']} mm sheath")
    
    if construction:
        components.append("construction: " + ", ".join(construction))
    
    # Add table context
    components.append(f"from page {meta['page']} table {meta['table_index']}")
    
    embedding_text = ". ".join(components)
    embedding = model.encode(embedding_text)
    
    return embedding, embedding_text

def create_table_context_embedding(records, meta):
    """Create embedding for the entire table context"""
    if not records:
        return None, ""
    
    # Analyze table content
    areas = [r.get('conductor_nominal_area_mm2') for r in records if r.get('conductor_nominal_area_mm2')]
    min_area = min(areas) if areas else None
    max_area = max(areas) if areas else None
    
    table_description = f"Table on page {meta['page']} containing {len(records)} cable specifications"
    if min_area and max_area:
        table_description += f" with conductor sizes from {min_area} to {max_area} sq mm"
    
    # Add technical focus
    technical_features = []
    if any(r.get('current_rating_amps') for r in records):
        technical_features.append("current ratings")
    if any(r.get('overall_weight_kg_per_km') for r in records):
        technical_features.append("weight specifications")
    if any(r.get('approx_overall_diameter_mm') for r in records):
        technical_features.append("dimensional data")
    
    if technical_features:
        table_description += f". Includes {', '.join(technical_features)}."
    
    embedding = model.encode(table_description)
    return embedding, table_description

def table_to_records(df, meta):
    df.columns = [re.sub(r'\s+','_',str(c).strip().lower()) for c in df.columns]
    records = []
    
    for _, row in df.iterrows():
        rec = {k: (v if pd.notna(v) else "") for k,v in row.items()}
        
        # Enhanced field mapping with more patterns
        rec_mapped = {
            "conductor_nominal_area_mm2": normalize_numeric(
                rec.get("conductor_nominal_area_(sq._mm)") or 
                rec.get("conductor_nominal_area_(sq._mm)") or 
                rec.get("conductor_nominal_area_(sq. mm)") or 
                rec.get("conductor_nominal_area_(sq.mm)") or 
                rec.get("nominal_area_(sq._mm)") or 
                rec.get("nominal_area") or
                rec.get("size") or
                rec.get("area")
            ),
            "insulation_thickness_mm": normalize_numeric(
                rec.get("nominal_insulation_thickness_(mm)") or 
                rec.get("nominal_insulation_thickness_mm") or
                rec.get("insulation_thickness") or
                rec.get("insulation")
            ),
            "outer_sheath_thickness_mm": normalize_numeric(
                rec.get("nominal_outer_sheath_thickness_(mm)") or 
                rec.get("nominal_outer_sheath_thickness_mm") or
                rec.get("sheath_thickness") or
                rec.get("outer_sheath")
            ),
            "approx_overall_diameter_mm": normalize_numeric(
                rec.get("approx._overall_diameter_(mm)") or 
                rec.get("approx._overall_diameter_mm") or 
                rec.get("approx._overall_dimeter_(mm)") or
                rec.get("overall_diameter") or
                rec.get("diameter")
            ),
            "overall_weight_kg_per_km": normalize_numeric(
                rec.get("overall_weight_approx._(kgs.km)") or 
                rec.get("overall_weight_approx_(kgs.km)") or 
                rec.get("overall_weight") or
                rec.get("weight") or
                rec.get("weight_kg_km")
            ),
            "current_rating_amps": normalize_numeric(
                rec.get("current_rating_(amps.)") or 
                rec.get("current_rating_(amps)") or 
                rec.get("current_rating") or
                rec.get("rating") or
                rec.get("amps")
            ),
            "raw_row": rec,
            "table_meta": meta
        }
        
        # Generate embeddings for each record
        record_id = generate_record_id(rec_mapped, meta)
        embedding, embedding_text = create_record_embedding(rec_mapped, meta)
        
        rec_mapped["record_id"] = record_id
        rec_mapped["embedding"] = embedding.tolist()  # Convert to list for JSON
        rec_mapped["embedding_text"] = embedding_text
        
        records.append(rec_mapped)
    
    return records

def process_pdf_with_embeddings():
    all_records = []
    table_contexts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if not tables:
                continue
                
            for t_idx, table in enumerate(tables):
                df = pd.DataFrame(table[1:], columns=table[0])
                if df.shape[0] < 1:
                    continue
                    
                meta = {"page": i, "table_index": t_idx}
                recs = table_to_records(df, meta)
                
                # Create table-level context embedding
                if recs:
                    table_embedding, table_description = create_table_context_embedding(recs, meta)
                    table_context = {
                        "table_meta": meta,
                        "record_count": len(recs),
                        "table_embedding": table_embedding.tolist() if table_embedding is not None else None,
                        "table_description": table_description,
                        "record_ids": [r["record_id"] for r in recs]
                    }
                    table_contexts.append(table_context)
                
                all_records.extend(recs)

    return all_records, table_contexts

# Process the PDF
print("Processing PDF and generating embeddings...")
all_records, table_contexts = process_pdf_with_embeddings()

# Save results
output_data = {
    "records": all_records,
    "table_contexts": table_contexts,
    "embedding_model": "all-MiniLM-L6-v2",
    "total_records": len(all_records),
    "total_tables": len(table_contexts)
}

with open(outdir / "havells_catalogue_with_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(all_records)} records from {len(table_contexts)} tables")
print(f"Saved to {outdir/'havells_catalogue_with_embeddings.json'}")

# Create a simplified version for vector storage
def create_vector_ready_data(records, table_contexts):
    """Create data optimized for vector database storage"""
    vectors = []
    
    # Add record embeddings
    for record in records:
        vectors.append({
            "id": record["record_id"],
            "embedding": record["embedding"],
            "text": record["embedding_text"],
            "metadata": {
                "type": "cable_record",
                "conductor_area_mm2": record.get("conductor_nominal_area_mm2"),
                "current_rating_amps": record.get("current_rating_amps"),
                "page": record["table_meta"]["page"],
                "table_index": record["table_meta"]["table_index"]
            }
        })
    
    # Add table context embeddings
    for table_ctx in table_contexts:
        if table_ctx["table_embedding"]:
            vectors.append({
                "id": f"table_{table_ctx['table_meta']['page']}_{table_ctx['table_meta']['table_index']}",
                "embedding": table_ctx["table_embedding"],
                "text": table_ctx["table_description"],
                "metadata": {
                    "type": "table_context",
                    "page": table_ctx["table_meta"]["page"],
                    "table_index": table_ctx["table_meta"]["table_index"],
                    "record_count": table_ctx["record_count"]
                }
            })
    
    return vectors

vector_data = create_vector_ready_data(all_records, table_contexts)
with open(outdir / "havells_vectors.json", "w", encoding="utf-8") as f:
    json.dump(vector_data, f, indent=2, ensure_ascii=False)

print(f"Created {len(vector_data)} vector entries -> {outdir/'havells_vectors.json'}")