# FHE Studio API

[FHE-Studio UI](https://github.com/artifirm/fhe-studio-ui) and [FHE-Studio API](https://github.com/artifirm/fhe-studio-api)  is an IDE to develop encrypted programs called circuits in the Python language

## Fully Homomorphic Encryption
Fully Homomorphic Encryption (FHE) is a groundbreaking cryptographic technique that allows computations to be performed on encrypted data without the need to decrypt it first. This means that data can remain confidential while still being processed, opening up new possibilities for secure data outsourcing and privacy-preserving computations. 

## Cloud 
IDE is freely available at https://fhe-studio.com, You need a Gmail account to log in

## Docker
[The fhe-studio image is here.](https://hub.docker.com/r/alextmn/fhe-studio)
Then go to http://localhost:5000 and log in as default user

`docker pull alextmn/fhe-studio:v1`
`docker run -p 5000:5000 --rm alextmn/fhe-studio:v1`

Then go to http://localhost:5000 and log in as default user




## How to Run
`docker-compose up --build`
Then run [FHE-Studio UI](https://github.com/artifirm/fhe-studio-ui)docker run 