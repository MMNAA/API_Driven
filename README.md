------------------------------------------------------------------------------------------------------
ATELIER API-DRIVEN INFRASTRUCTURE
------------------------------------------------------------------------------------------------------
L’idée en 30 secondes : **Orchestration de services AWS via API Gateway et Lambda dans un environnement émulé**.  
Cet atelier propose de concevoir une architecture **API-driven** dans laquelle une requête HTTP déclenche, via **API Gateway** et une **fonction Lambda**, des actions d’infrastructure sur des **instances EC2**, le tout dans un **environnement AWS simulé avec LocalStack** et exécuté dans **GitHub Codespaces**. L’objectif est de comprendre comment des services cloud serverless peuvent piloter dynamiquement des ressources d’infrastructure, indépendamment de toute console graphique.Cet atelier propose de concevoir une architecture API-driven dans laquelle une requête HTTP déclenche, via API Gateway et une fonction Lambda, des actions d’infrastructure sur des instances EC2, le tout dans un environnement AWS simulé avec LocalStack et exécuté dans GitHub Codespaces. L’objectif est de comprendre comment des services cloud serverless peuvent piloter dynamiquement des ressources d’infrastructure, indépendamment de toute console graphique.
  
-------------------------------------------------------------------------------------------------------
Séquence 1 : Codespace de Github
-------------------------------------------------------------------------------------------------------
Objectif : Création d'un Codespace Github  
Difficulté : Très facile (~5 minutes)
-------------------------------------------------------------------------------------------------------
RDV sur Codespace de Github : <a href="https://github.com/features/codespaces" target="_blank">Codespace</a> **(click droit ouvrir dans un nouvel onglet)** puis créer un nouveau Codespace qui sera connecté à votre Repository API-Driven.
  
---------------------------------------------------
Séquence 2 : Création de l'environnement AWS (LocalStack)
---------------------------------------------------
Objectif : Créer l'environnement AWS simulé avec LocalStack  
Difficulté : Simple (~5 minutes)
---------------------------------------------------

Dans le terminal du Codespace copier/coller les codes ci-dessous etape par étape :  

**Installation de l'émulateur LocalStack**  
```
sudo -i mkdir rep_localstack
```
```
sudo -i python3 -m venv ./rep_localstack
```
```
sudo -i pip install --upgrade pip && python3 -m pip install localstack && export S3_SKIP_SIGNATURE_VALIDATION=0
```
```
localstack start -d
```
**vérification des services disponibles**  
```
localstack status services
```
**Réccupération de l'API AWS Localstack** 
Votre environnement AWS (LocalStack) est prêt. Pour obtenir votre AWS_ENDPOINT cliquez sur l'onglet **[PORTS]** dans votre Codespace et rendez public votre port **4566** (Visibilité du port).
Réccupérer l'URL de ce port dans votre navigateur qui sera votre ENDPOINT AWS (c'est à dire votre environnement AWS).
Conservez bien cette URL car vous en aurez besoin par la suite.  

Pour information : IL n'y a rien dans votre navigateur et c'est normal car il s'agit d'une API AWS (Pas un développement Web type UX).

---------------------------------------------------
Séquence 3 : Exercice
---------------------------------------------------
Objectif : Piloter une instance EC2 via API Gateway
Difficulté : Moyen/Difficile (~2h)
---------------------------------------------------  
Votre mission (si vous l'acceptez) : Concevoir une architecture **API-driven** dans laquelle une requête HTTP déclenche, via **API Gateway** et une **fonction Lambda**, lancera ou stopera une **instance EC2** déposée dans **environnement AWS simulé avec LocalStack** et qui sera exécuté dans **GitHub Codespaces**. [Option] Remplacez l'instance EC2 par l'arrêt ou le lancement d'un Docker.  

**Architecture cible :** Ci-dessous, l'architecture cible souhaitée.   
  
![Screenshot Actions](API_Driven.png)   
  
---------------------------------------------------  
## Processus de travail (résumé)

1. Installation de l'environnement Localstack (Séquence 2)
2. Création de l'instance EC2
3. Création des API (+ fonction Lambda)
4. Ouverture des ports et vérification du fonctionnement

---------------------------------------------------
Séquence 4 : Documentation  
Difficulté : Facile (~30 minutes)
---------------------------------------------------
**Complétez et documentez ce fichier README.md** pour nous expliquer comment utiliser votre solution.  
Faites preuve de pédagogie et soyez clair dans vos expliquations et processus de travail.  

Orchestration de services AWS via API Gateway et Lambda (LocalStack)

Objectif

Ce projet met en place une architecture **API-driven** permettant de piloter une instance EC2 via une requête HTTP.

Une requête envoyée à une API déclenche une fonction Lambda qui démarre ou arrête une instance EC2, le tout dans un environnement AWS simulé avec LocalStack.

---

Architecture

Flux de traitement :

```
Client HTTP (curl)
        ↓
API Gateway
        ↓
AWS Lambda
        ↓
EC2 (LocalStack)
```

---

Technologies utilisées

* GitHub Codespaces
* LocalStack (simulation AWS)
* AWS CLI
* AWS Lambda (Python)
* API Gateway
* EC2 (simulé)

---

Installation et configuration

1. Lancer LocalStack

```bash
localstack start -d
```

---

2. Configuration AWS CLI

```bash
aws configure
```

Valeurs utilisées :

* Access Key : test
* Secret Key : test
* Region : us-east-1

---

Mise en place de l’infrastructure

1. Création d’une AMI

```bash
aws ec2 register-image \
  --name "test-ami" \
  --description "test image" \
  --architecture x86_64 \
  --root-device-name "/dev/sda1" \
  --block-device-mappings DeviceName="/dev/sda1",Ebs={VolumeSize=8} \
  --endpoint-url=http://localhost:4566
```

---

2. Création d’une instance EC2

```bash
aws ec2 run-instances \
  --image-id <AMI_ID> \
  --count 1 \
  --instance-type t2.micro \
  --endpoint-url=http://localhost:4566
```

---

3. Récupération de l’InstanceId

```bash
aws ec2 describe-instances \
  --endpoint-url=http://localhost:4566
```

---

Déploiement de la Lambda

Code principal

```python
import boto3
import os
import json
from botocore.config import Config

def lambda_handler(event, context):
    config = Config(connect_timeout=2, read_timeout=2, retries={'max_attempts': 0})

    ec2 = boto3.client(
        "ec2",
        endpoint_url="http://localhost.localstack.cloud:4566",
        region_name="us-east-1",
        config=config
    )

    instance_id = os.environ.get("INSTANCE_ID")

    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = event

    action = body.get("action", "start")

    if action == "start":
        ec2.start_instances(InstanceIds=[instance_id])
        return {"status": "started"}

    elif action == "stop":
        ec2.stop_instances(InstanceIds=[instance_id])
        return {"status": "stopped"}

    return {"status": "unknown"}
```

---

Déploiement

```bash
zip function.zip lambda_function.py
```

```bash
aws lambda create-function \
  --function-name control-ec2 \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --environment "Variables={INSTANCE_ID=<INSTANCE_ID>}" \
  --endpoint-url=http://localhost:4566
```

---

Mise en place de l’API Gateway

Création API

```bash
aws apigateway create-rest-api --name "ec2-api"
```

---

Intégration Lambda

* Méthode : POST
* Type : AWS
* Mapping : JSON → Lambda

---

Déploiement

```bash
aws apigateway create-deployment \
  --rest-api-id <API_ID> \
  --stage-name dev \
  --endpoint-url=http://localhost:4566
```

---

Test de l’API

```bash
curl -X POST \
http://localhost:4566/restapis/<API_ID>/dev/_user_request_/ec2 \
-d '{"action":"start"}'
```

---

Résultat attendu

```json
{"status": "started"}
```

---

Difficultés rencontrées

* Gestion du réseau entre Lambda et LocalStack (`localhost` vs container)
* Timeout de Lambda
* Mapping des données dans API Gateway
* Configuration des réponses API Gateway (method + integration response)

---

Améliorations possibles

* Gestion des erreurs plus avancée
* Ajout d’un système de logs
* Interface web pour piloter les actions
* Support de plusieurs instances EC2

---

Conclusion

Ce projet démontre la mise en place d’une architecture serverless pilotée par API, permettant de contrôler dynamiquement des ressources d’infrastructure.

L’utilisation de LocalStack permet de reproduire un environnement AWS complet sans dépendre du cloud réel.


---------------------------------------------------
Evaluation
---------------------------------------------------
Cet atelier, **noté sur 20 points**, est évalué sur la base du barème suivant :  
- Repository exécutable sans erreur majeure (4 points)
- Fonctionnement conforme au scénario annoncé (4 points)
- Degré d'automatisation du projet (utilisation de Makefile ? script ? ...) (4 points)
- Qualité du Readme (lisibilité, erreur, ...) (4 points)
- Processus travail (quantité de commits, cohérence globale, interventions externes, ...) (4 points) 
