### Microservices Application for Visualization, Processing, and Uploading Geospatial Files

This repository is part of a larger application that follows a microservices architecture. Currently, it includes an API developed using the Echo framework in Go (Golang), which is the first service implemented. The API is responsible for reading, processing, and uploading geospatial files in KML format to a bucket on Google Cloud Platform (GCP). Once a file is uploaded, the system triggers a message via GCP Pub/Sub to notify other services about the availability of the new geospatial file.

The application is designed to streamline the integration of services that need to handle geospatial data, ensuring that the upload and notification processes occur efficiently. Firebase authentication provides robust access control, while GCP and Pub/Sub integration ensure scalability and real-time communication between the processing service.

Key features:

- User authentication with Firebase.
- KML file processing.
- Upload of KML files to a GCP bucket.
- Pub/Sub message emission for notifying new files.
- This solution is ideal for systems that require real-time integration with geospatial data, leveraging Google Cloud's infrastructure.

### Aplicação de Microserviços para Visualização, Processamento e Upload de Arquivos Geoespaciais

Este repositório faz parte de uma aplicação maior que segue uma arquitetura de microserviços. Atualmente, conta com uma API desenvolvida utilizando o framework Echo em Go (Golang), sendo o primeiro serviço implementado. A API é responsável por ler, processar e fazer o upload de arquivos geoespaciais no formato KML para um bucket no Google Cloud Platform (GCP). Assim que um arquivo é enviado, o sistema dispara uma mensagem via GCP Pub/Sub para notificar outros serviços sobre a disponibilidade do novo arquivo geoespacial.

A aplicação foi projetada para facilitar a integração de serviços que precisam lidar com dados geoespaciais, garantindo que os processos de upload e notificação ocorram de forma eficiente. A autenticação via Firebase oferece um controle de acesso robusto, enquanto a integração com GCP e Pub/Sub garante escalabilidade e comunicação em tempo real entre os serviços de processamento.

**Principais funcionalidades:**

- Autenticação de usuários com Firebase.
- Processamento de arquivos KML.
- Upload de arquivos KML para um bucket GCP.
- Emissão de mensagens via Pub/Sub para notificação de novos arquivos.

Essa solução é ideal para sistemas que exigem integração em tempo real com dados geoespaciais, aproveitando a infraestrutura do Google Cloud.
