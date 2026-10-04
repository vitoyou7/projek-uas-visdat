# Pemakaian:
#   pip install pypdf Sastrawi scikit-learn networkx
#   python preprocess_brs.py folder_pdf_brs      -> menghasilkan brs_textmining.json
#
# Tahap pra-pemrosesan teks (untuk Metodologi makalah):
#   1) ekstraksi teks PDF (pypdf)  2) case folding  3) tokenisasi (hanya huruf, panjang > 3)
#   4) penghapusan stopword Bahasa Indonesia (Sastrawi + stopword domain)
#   5) stemming Bahasa Indonesia (Sastrawi)  6) penghapusan stopword ulang pada hasil stem
import re,sys,glob,json,collections
from datetime import date,timedelta
from pypdf import PdfReader
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import networkx as nx, numpy as np

K_TOPIK=5; TOP=120
# kata pengisi (boilerplate) BRS: nama bulan, angka dalam huruf, dan kata tabel/penomoran
BULAN='januari februari maret april mei juni juli agustus september oktober november desember'.split()
ANGKA='satu dua tiga empat lima enam tujuh delapan sembilan sepuluh sebelas belas puluh ratus ribu juta'.split()
BOILER='tabel gambar grafik lampiran halaman nomor nama kode keterangan catatan sumber daftar tercatat catat penghitungan hitung'.split()
ROMAWI=re.compile(r'^m{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$')   # angka romawi (mis. xxix, viii)
HAPUS_NAMA_WILAYAH=True   # ubah ke True bila ingin topik LDA tidak didominasi nama daerah
BL={'juli':7,'agustus':8,'september':9}; LB={7:'Jul 2026',8:'Agu 2026',9:'Sep 2026'}
STOP=set(StopWordRemoverFactory().get_stop_words())|set('bps badan pusat statistik berita resmi persen provinsi tahun bulan juli agustus september year month yoy mtm ctc dibandingkan terhadap dengan pada yang dan dari sebesar terjadi andil banding'.split())
if HAPUS_NAMA_WILAYAH:
    STOP|=set('aceh sumatera utara barat selatan riau jambi bengkulu lampung bangka belitung kepulauan jawa banten yogyakarta bali nusa tenggara kalimantan tengah timur sulawesi gorontalo maluku papua daya pegunungan jakarta dki indonesia'.split())
STOP|=set(BULAN)|set(ANGKA)|set(BOILER)

docs=[]
for f in sorted(glob.glob(sys.argv[1]+'/**/*.pdf',recursive=True)):
    t=' '.join((p.extract_text() or '') for p in PdfReader(f).pages)
    m=re.search(r'(\d{1,2})\s+(Juli|Agustus|September)\s+2026',t)
    d=date(2026,BL[m.group(2).lower()],int(m.group(1))) if m else date(2026,7,1)
    docs.append((d,t))
print(len(docs),'dokumen')
if not docs: sys.exit('Tidak ada PDF ditemukan di folder tersebut.')

STEMMER=StemmerFactory().create_stemmer(); CACHE={}; SURF=collections.defaultdict(collections.Counter)
def stem(w):
    if w not in CACHE: CACHE[w]=STEMMER.stem(w)
    return CACHE[w]
def clean(t):
    toks=[w for w in re.sub(r'[^a-z\s]',' ',t.lower()).split() if len(w)>3 and w not in STOP and not ROMAWI.match(w)]  # case folding, tokenisasi, stopword, angka romawi
    out=[]
    for w in toks:
        s=stem(w)                                    # stemming
        if len(s)>3 and s not in STOP and not ROMAWI.match(s):               # stopword ulang pada kata dasar
            out.append(s); SURF[s][w]+=1
    return ' '.join(out)
C=[]
for i,(_,t) in enumerate(docs):
    C.append(clean(t))
    if (i+1)%10==0: print('  diproses',i+1,'/',len(docs),'dokumen (stemming)')
D=[d for d,_ in docs]
# agar tampilan mudah dibaca, tiap kata dasar ditampilkan dengan bentuk asli yang paling sering muncul
LABEL={}; USED=set()
for s,c in sorted(SURF.items(),key=lambda x:-sum(x[1].values())):
    l=c.most_common(1)[0][0]
    while l in USED: l+="'"
    USED.add(l); LABEL[s]=l
lab=lambda s:LABEL.get(s,s)

def top_words(idx):
    cv=CountVectorizer(); X=cv.fit_transform([C[i] for i in idx]); s=np.asarray(X.sum(0)).ravel()
    return [{'w':lab(cv.get_feature_names_out()[j]),'f':int(s[j])} for j in s.argsort()[::-1][:TOP]]
words={'Semua':top_words(range(len(C)))}
for mth,lb in LB.items():
    ix=[i for i,d in enumerate(D) if d.month==mth]
    if ix: words[lb]=top_words(ix)
# istilah yang muncul di >50% dokumen dianggap pengisi dan tidak dipakai untuk LDA
cv=CountVectorizer(min_df=3,max_df=.5); X=cv.fit_transform(C); fn=cv.get_feature_names_out()
lda=LatentDirichletAllocation(K_TOPIK,random_state=1,max_iter=40).fit(X); th=lda.transform(X)
topics=[]
for k,c in enumerate(lda.components_):
    c=c/c.sum(); o=c.argsort()[::-1][:12]
    topics.append({'id':k,'label':', '.join(lab(fn[j]) for j in o[:3]),'words':[[lab(fn[j]),round(float(c[j]),4)] for j in o]})
wk=lambda d:d-timedelta(days=d.weekday())
keys=sorted({wk(d) for d in D}); trend={'x':[k.strftime('%d %b')for k in keys],'y':[[float(np.mean([th[i][t] for i,d in enumerate(D) if wk(d)==k])) for k in keys] for t in range(K_TOPIK)]}
bv=CountVectorizer(ngram_range=(2,2),min_df=4); BX=bv.fit_transform(C); bs=np.asarray(BX.sum(0)).ravel(); bn=bv.get_feature_names_out()
G=nx.Graph()
for j in bs.argsort()[::-1][:150]:
    a,b=bn[j].split(); G.add_edge(a,b,weight=int(bs[j]))
pos=nx.spring_layout(G,seed=1,k=.8,weight='weight'); grp={}
for g,cm in enumerate(nx.community.greedy_modularity_communities(G)):
    for n in cm: grp[n]=g
net={'nodes':[{'id':lab(n),'x':float(pos[n][0]),'y':float(pos[n][1]),'deg':G.degree(n),'grp':grp[n]} for n in G],'edges':[{'s':lab(a),'t':lab(b),'w':d['weight']} for a,b,d in G.edges(data=True)]}
json.dump({'words':words,'topics':topics,'trend':trend,'net':net},open('brs_textmining.json','w'),ensure_ascii=False)
print('selesai -> brs_textmining.json')