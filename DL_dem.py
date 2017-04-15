import pandas as pd
import os
import wget
import zipfile
import glob

file = '/home/UA/jschroder/Downloads/ned_111.csv'
df = pd.read_csv(file,index_col=0)

DL_NED1 = '/workspace/Shared/Users/jschroder/TMP/DL_YQ'
if not os.path.exists(DL_NED1): os.makedirs(DL_NED1)

for i,k in zip(df.downloadURL , range(1,len(df.downloadURL)+1)) :
    print 'downloading %s out of %s' %(k , len(df.downloadURL))
    wget.download(i,out=DL_NED1)
    

for j in os.listdir(DL_NED1):
    zfile = zipfile.ZipFile(os.path.join(DL_NED1,j))
    zfile.extractall(DL_NED1)
a = DL_NED1

ls = [ os.path.join(a,i) for i in glob.glob(os.path.join(a,'*.img'))    ]
tiles = ' '.join(map(str,ls))
full = os.path.join(a,'full.img')
full2 = os.path.join(a,'full3.img')
fulltiff =os.path.join(a,'full3.tif')