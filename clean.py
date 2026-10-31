import pandas as pd, numpy as np
raw = pd.read_csv('/mnt/user-data/uploads/uae-housing_dataset.csv')
log = {'raw_rows': len(raw)}
df = raw.rename(columns={'propert_type':'property_type','area(sqft)':'area_sqft','address':'location'}).copy()

# 1. exact duplicates
log['exact_duplicates_removed'] = int(df.duplicated().sum())
df = df.drop_duplicates()

# 2. column-shift rows (bathroom holds an area value)
bad = df.bathroom.str.contains('sqft')
log['shifted_rows_removed'] = int(bad.sum())
df = df[~bad]

# 3. numeric parsing
df['price_aed'] = df.price.str.replace(',','').astype(float)
df['area_sqft'] = df.area_sqft.str.replace(' sqft','').str.replace(',','').astype(float)
df['bedrooms'] = df.bedroom.str.extract(r'(\d+)').astype(float).fillna(0).astype(int)   # Studio = 0
df['bathrooms'] = df.bathroom.str.extract(r'(\d+)').astype(int)
df['is_studio'] = (df.bedroom=='Studio')

# 4. impossible area (area == price, 13.1M sqft)
bad = df.area_sqft > 100000
log['impossible_area_removed'] = int(bad.sum())
df = df[~bad]

# 5. derived fields
df['price_per_sqft'] = (df.price_aed/df.area_sqft).round(1)
df['handover_year'] = df.handover.str[-4:].astype(int)
df['handover_quarter'] = df.handover.str[:2]
df['bedroom_label'] = np.where(df.is_studio,'Studio',df.bedrooms.astype(str)+' BR')
df['price_band'] = pd.cut(df.price_aed,[0,1e6,2e6,5e6,1e7,np.inf],labels=['<1M','1-2M','2-5M','5-10M','10M+']).astype(str)

# 6. governance flag: rows kept but flagged
df['dq_flag'] = np.where((df.property_type.isin(['Residential Building','Villa Compound'])),'non_standard_type',
                 np.where((df.completion_status=='Ready')&(df.handover_year>=2027),'ready_but_future_handover','ok'))
log['flag_counts'] = df.dq_flag.value_counts().to_dict()

out = df[['price_aed','area_sqft','price_per_sqft','bedrooms','bedroom_label','bathrooms','property_type','location',
          'project_name','furnishing','completion_status','handover','handover_year','handover_quarter','price_band','dq_flag']]
out.insert(0,'listing_id',range(1,len(out)+1))
out.to_csv('/mnt/user-data/outputs/uae-housing-dashboard/uae_housing_clean.csv',index=False)
log['clean_rows']=len(out)
print(log)

# headline KPIs
k=out[out.dq_flag!='non_standard_type']
print('listings',len(k),'median price',k.price_aed.median(),'median ppsf',k.price_per_sqft.median(),'median area',k.area_sqft.median())
print(k.groupby('completion_status').price_per_sqft.median())
print(k.groupby('property_type').price_per_sqft.median())
t=k.groupby('location').agg(n=('listing_id','count'),ppsf=('price_per_sqft','median'),price=('price_aed','median'))
print(t[t.n>=30].sort_values('ppsf',ascending=False).head(8)); print(t[t.n>=30].sort_values('ppsf').head(5))
print(t.sort_values('n',ascending=False).head(5))
print(k.groupby('furnishing').price_per_sqft.median())
print(k.groupby('bedroom_label').agg(n=('listing_id','count'),price=('price_aed','median')))
print(k[k.completion_status=='Off-Plan'].handover_year.value_counts().sort_index())
