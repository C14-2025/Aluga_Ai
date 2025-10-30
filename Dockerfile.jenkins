# Dockerfile para rodar o servidor Jenkins puro
FROM jenkins/jenkins:lts

# Instala mailutils (opcional, só se for usar notificação por email)
USER root
RUN apt-get update && apt-get install -y mailutils && apt-get clean

USER jenkins
# Jenkins será iniciado automaticamente ao rodar o container