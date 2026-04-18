# K8s Config Generator

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Kubernetes](https://img.shields.io/badge/kubernetes-manifests-326ce5.svg)
![CLI](https://img.shields.io/badge/interface-CLI-lightgrey.svg)
![DevOps](https://img.shields.io/badge/DevOps-automation-green.svg)

Профессиональная CLI-утилита для быстрой генерации production-ready Kubernetes манифестов. Создает полноценные конфигурации для развертывания приложений в кластере Kubernetes с поддержкой современных DevOps практик.

## 🚀 Возможности

### 🎯 **Основные функции**
- **Интерактивный интерфейс:** Удобное консольное меню с библиотекой `questionary`
- **Динамическая генерация:** Создание валидных YAML-файлов без бойлерплейта
- **Продвинутая конфигурация:** Поддержка health checks, ресурсов, Ingress

### 🔧 **Kubernetes компоненты**
- **Deployment:** С настраиваемыми репликами, портами, health checks и ресурсами
- **Service:** ClusterIP с именованными портами и правильными labels
- **Ingress:** Внешний доступ через NGINX с настраиваемым путем
- **PostgreSQL:** StatefulSet + Service для баз данных (опционально)
- **Kustomization:** Управление конфигурациями и версиями образов
- **ConfigMap:** Генерация из .env файлов для переменных окружения

### 🏗️ **DevOps особенности**
- **Health Checks:** Liveness и readiness probes для мониторинга
- **Ресурсы:** CPU/memory requests и limits
- **Labels:** Совместимость с платформой (app.kubernetes.io/*)
- **Структура:** Файлы называются как в вашей платформе (svc.yaml)

## 📋 Интерактивные вопросы

Утилита последовательно задает вопросы:
1. **Имя приложения** - для создания ресурсов
2. **Количество реплик** - масштабирование (по умолчанию 3)
3. **Порт приложения** - containerPort (по умолчанию 8080)
4. **PostgreSQL** - нужна ли база данных
5. **Ingress** - внешний доступ и путь
6. **Health Checks** - мониторинг состояния
7. **Ресурсы** - CPU/memory лимиты
8. **ConfigMap** - генерация из .env файла

## 📁 Структура выходных файлов

```
k8s_manifests/app-name/
├── deployment.yaml      # с health checks и ресурсами
├── svc.yaml            # с именованными портами
├── ingress.yaml        # опционально
├── kustomization.yaml   # всегда
├── app-name.env         # опционально
├── postgres.yaml        # опционально
├── postgres-statefulset.yaml
└── postgres-service.yaml
```

## ⚙️ Установка и запуск

### 📦 Установка зависимостей
```bash
pip install -r requirements.txt
```

### 🚀 Запуск генератора
```bash
python k8s_generator.py
```

### 🚀 Развертывание в Kubernetes
```bash
kubectl apply -k k8s_manifests/app-name/
```

## 📋 Требования

- **Python 3.9+**
- **Kubernetes кластер** (для развертывания)
- **kubectl** (настроенный на ваш кластер)

## 🛠️ Зависимости

- `questionary==2.1.1` - интерактивный CLI
- `PyYAML==6.0.3` - работа с YAML файлами

## 🎯 Пример использования

```bash
$ python k8s_generator.py
? Enter application name (app name): my-app
? Number of replicas: 3
? Which port does the application use (containerPort)? 8080
? Do you need PostgreSQL database? No
? Do you need external access (Ingress)? Yes
? Enter ingress path (leave empty for default): /my-app
? Do you want to add health checks (liveness/readiness probes)? Yes
? Do you want to set resource limits (CPU/memory)? Yes
? CPU request (m): 100m
? CPU limit (m): 500m
? Memory request (Mi): 128Mi
? Memory limit (Mi): 512Mi
? Do you want to generate ConfigMap from .env file? Yes

✅ Манифесты успешно сгенерированы в папке k8s_manifests/my-app!
```

## 🔧 Концепция объяснения

### Health Checks
- **Liveness Probe:** Проверяет, живо ли приложение (перезапуск если нет)
- **Readiness Probe:** Проверяет, готово ли приложение принимать трафик

### Ingress
- **Внешний доступ:** Позволяет пользователям обращаться к приложению извне
- **Маршрутизация:** Распределяет трафик между сервисами по URL путям

### ConfigMap
- **Конфигурация:** Хранит переменные окружения отдельно от кода
- **Гибкость:** Легко менять настройки без пересборки образа

## 📄 Лицензия

MIT License - свободно использовать в коммерческих проектах