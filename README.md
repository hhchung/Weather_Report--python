# Weather Report--python

##Prerequisite:	
May need to install some python module: (requests , BeautifulSoup4)

```sh	
  python3 -m  pip install --user requests
  python3 -m  pip install --user BeautifulSoup4
```

##Some simple usage examples	

 weather.py [-h] [-l location] [-u unit] [-a | -c | -d day] [-s]
	
    a.> python3 weather -h 
    b.> python3 weather.py -l Hsinchu -u c -c 
    c.> python3 weather.py -l Hsinchu -u c -a 
    d.> python3 weather.py -l Hsinchu -u c -d 2
    e.> python3 weather.py -l Hsinchu -c -s 
    f.> python3 weather.py -l taipei,hsinchu,tainan -a

    g.config.py format
	  '#': represent comment
	  LOCATION="hsinchu , taipei , tainan" #can using many citys and seperated by comma
	  UNIT="f" or UNIT="c"
