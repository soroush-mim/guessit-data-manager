## Data Manager
this repository contains a flask server that implements REST API and functionality for writing and testing templates and generating question from the given templates and data. this questions used in a question game named [whoknows](www.whoknows.ir)

![whoknows logo](http://s8.picofile.com/file/8361648192/logo_5_3.png)

## How to install?
Setting up is simple, just follow these steps.

### Python :

1. Install python and pip and git:
```sh
apt install git python3 python3-pip
```

2. Clone the repository:
```sh
git clone https://github.com/danialkeimasi/whoknows-template-manager
```

3. Go to repository folder:
```sh
cd whoknows-template-manager
```

4. Install dependencies:
```sh
pip install -r requirements.txt
```

5. Start server:
```sh
python3 app.py
```

### Docker :

1. Clone the repository:
```sh
git clone https://github.com/danialkeimasi/whoknows-template-manager
```

2. Go to repository folder:
```sh
cd whoknows-template-manager
```

3. Build image from dockerfile:
```sh
docker build -t whoknows-template-manager
```

4. Run docker image:
```sh
docker run -it whoknows-template-manager
```


## What it does?


## How to use?
API documentation url : 


## Who is in charge?
- Mohammad Parsian
- Soroush Mahdi
- Danial Keimasi
