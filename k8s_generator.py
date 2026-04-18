#!/usr/bin/env python3
"""
K8s Config Generator - Interactive CLI utility for generating Kubernetes manifests
Author: Senior DevOps Engineer
"""

import os
import yaml
import questionary
from pathlib import Path


def generate_deployment_manifest(app_name: str, replicas: int, container_port: int, 
                             health_checks: bool = False, resources: dict = None) -> dict:
    """Generate Kubernetes Deployment manifest"""
    deployment = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': app_name,
            'labels': {
                'app.kubernetes.io/name': app_name,
                'app.kubernetes.io/part-of': 'ziak'
            }
        },
        'spec': {
            'replicas': replicas,
            'selector': {
                'matchLabels': {
                    'app.kubernetes.io/name': app_name
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app.kubernetes.io/name': app_name,
                        'app.kubernetes.io/part-of': 'ziak'
                    }
                },
                'spec': {
                    'containers': [
                        {
                            'name': app_name,
                            'image': f'{app_name}:latest',
                            'ports': [
                                {
                                    'name': 'http',
                                    'containerPort': container_port,
                                    'protocol': 'TCP'
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    # Add health checks if enabled
    if health_checks:
        deployment['spec']['template']['spec']['containers'][0]['livenessProbe'] = {
            'httpGet': {
                'path': '/health/liveness',
                'port': 'http'
            },
            'initialDelaySeconds': 30,
            'periodSeconds': 10,
            'timeoutSeconds': 5,
            'failureThreshold': 3,
            'successThreshold': 1
        }
        deployment['spec']['template']['spec']['containers'][0]['readinessProbe'] = {
            'httpGet': {
                'path': '/health/readiness',
                'port': 'http'
            },
            'initialDelaySeconds': 5,
            'periodSeconds': 5,
            'timeoutSeconds': 3,
            'failureThreshold': 3,
            'successThreshold': 1
        }
    
    # Add resources if specified
    if resources:
        deployment['spec']['template']['spec']['containers'][0]['resources'] = resources
    
    return deployment


def generate_service_manifest(app_name: str, container_port: int) -> dict:
    """Generate Kubernetes Service manifest"""
    return {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': app_name,
            'labels': {
                'app.kubernetes.io/name': app_name,
                'app.kubernetes.io/part-of': 'ziak'
            }
        },
        'spec': {
            'type': 'ClusterIP',
            'selector': {
                'app.kubernetes.io/name': app_name
            },
            'ports': [
                {
                    'name': 'http',
                    'protocol': 'TCP',
                    'port': 80,
                    'targetPort': container_port
                }
            ]
        }
    }


def generate_ingress_manifest(app_name: str, ingress_path: str = None) -> dict:
    """Generate Kubernetes Ingress manifest"""
    if ingress_path is None:
        ingress_path = f'/{app_name}'
    
    return {
        'apiVersion': 'networking.k8s.io/v1',
        'kind': 'Ingress',
        'metadata': {
            'name': app_name,
            'annotations': {
                'nginx.ingress.kubernetes.io/proxy-read-timeout': '120'
            }
        },
        'spec': {
            'ingressClassName': 'nginx',
            'rules': [
                {
                    'http': {
                        'paths': [
                            {
                                'path': ingress_path,
                                'pathType': 'Prefix',
                                'backend': {
                                    'service': {
                                        'name': app_name,
                                        'port': {
                                            'name': 'http'
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }


def generate_kustomization_manifest(app_name: str, with_postgres: bool = False, with_configmap: bool = False) -> dict:
    """Generate Kustomization manifest"""
    kustomization = {
        'apiVersion': 'kustomize.config.k8s.io/v1beta1',
        'kind': 'Kustomization',
        'images': [
            {
                'name': app_name,
                'newTag': 'latest'
            }
        ],
        'labels': [
            {
                'pairs': {
                    'app.kubernetes.io/part-of': 'ziak',
                    'zyfra.com/product': 'ziak',
                    'zyfra.com/type': 'backend'
                },
                'includeTemplates': True
            },
            {
                'pairs': {
                    'app.kubernetes.io/name': app_name
                },
                'includeTemplates': True,
                'includeSelectors': True
            }
        ],
        'resources': [
            'deployment.yaml',
            'svc.yaml'
        ]
    }
    
    # Add PostgreSQL resources if needed
    if with_postgres:
        kustomization['resources'].extend(['postgres-statefulset.yaml', 'postgres-service.yaml'])
    
    # Add ConfigMap generator if needed
    if with_configmap:
        kustomization['configMapGenerator'] = [
            {
                'name': app_name,
                'envs': [f'{app_name}.env'],
                'options': {
                    'labels': {
                        'app.kubernetes.io/name': app_name
                    }
                }
            }
        ]
    
    return kustomization


def generate_env_file(app_name: str, output_dir: Path) -> None:
    """Generate basic .env file for the application"""
    env_content = f"""# Environment variables for {app_name}
CONTEXT_PATH=/{app_name}
ASPNETCORE_ENVIRONMENT=Production

# Add your application-specific environment variables here
# EXAMPLE_VAR=value
"""
    
    with open(output_dir / f'{app_name}.env', 'w', encoding='utf-8') as f:
        f.write(env_content)


def generate_postgres_manifests(app_name: str) -> tuple[dict, dict]:
    """Generate PostgreSQL StatefulSet and Service manifests"""
    
    # PostgreSQL StatefulSet
    postgres_statefulset = {
        'apiVersion': 'apps/v1',
        'kind': 'StatefulSet',
        'metadata': {
            'name': f'{app_name}-postgres',
            'labels': {
                'app': f'{app_name}-postgres'
            }
        },
        'spec': {
            'serviceName': f'{app_name}-postgres',
            'replicas': 1,
            'selector': {
                'matchLabels': {
                    'app': f'{app_name}-postgres'
                }
            },
            'template': {
                'metadata': {
                    'labels': {
                        'app': f'{app_name}-postgres'
                    }
                },
                'spec': {
                    'containers': [
                        {
                            'name': 'postgres',
                            'image': 'postgres:15',
                            'env': [
                                {
                                    'name': 'POSTGRES_DB',
                                    'value': f'{app_name}_db'
                                },
                                {
                                    'name': 'POSTGRES_USER',
                                    'value': 'postgres'
                                },
                                {
                                    'name': 'POSTGRES_PASSWORD',
                                    'value': 'postgres'
                                }
                            ],
                            'ports': [
                                {
                                    'containerPort': 5432
                                }
                            ],
                            'volumeMounts': [
                                {
                                    'name': 'postgres-storage',
                                    'mountPath': '/var/lib/postgresql/data'
                                }
                            ]
                        }
                    ]
                }
            },
            'volumeClaimTemplates': [
                {
                    'metadata': {
                        'name': 'postgres-storage'
                    },
                    'spec': {
                        'accessModes': ['ReadWriteOnce'],
                        'resources': {
                            'requests': {
                                'storage': '1Gi'
                            }
                        }
                    }
                }
            ]
        }
    }
    
    # PostgreSQL Service
    postgres_service = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': f'{app_name}-postgres',
            'labels': {
                'app': f'{app_name}-postgres'
            }
        },
        'spec': {
            'type': 'ClusterIP',
            'selector': {
                'app': f'{app_name}-postgres'
            },
            'ports': [
                {
                    'protocol': 'TCP',
                    'port': 5432,
                    'targetPort': 5432
                }
            ]
        }
    }
    
    return postgres_statefulset, postgres_service


def save_manifest_to_file(manifest: dict, file_path: Path) -> None:
    """Save manifest dictionary to YAML file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, indent=2)


async def main():
    """Main function to run the interactive CLI"""
    print("=== K8s Config Generator ===")
    print("Interactive Kubernetes manifest generator\n")
    
    # Interactive questions for user
    app_name = await questionary.text(
        "Enter application name (app name):",
        validate=lambda text: len(text.strip()) > 0 or "Application name cannot be empty"
    ).ask_async()
    
    replicas = await questionary.text(
        "Number of replicas:",
        default="3",
        validate=lambda text: text.isdigit() and int(text) > 0 or "Please enter a positive number"
    ).ask_async()
    replicas = int(replicas)
    
    container_port = await questionary.text(
        "Which port does the application use (containerPort)?",
        default="8080",
        validate=lambda text: text.isdigit() and 1 <= int(text) <= 65535 or "Please enter a valid port number (1-65535)"
    ).ask_async()
    container_port = int(container_port)
    
    need_postgres = await questionary.confirm(
        "Do you need PostgreSQL database?",
        default=False
    ).ask_async()
    
    need_ingress = await questionary.confirm(
        "Do you need external access (Ingress)?",
        default=True
    ).ask_async()
    
    ingress_path = None
    if need_ingress:
        ingress_path = await questionary.text(
            "Enter ingress path (leave empty for default):",
            default=f"/{app_name}"
        ).ask_async()
        if not ingress_path.strip():
            ingress_path = f"/{app_name}"
    
    need_health_checks = await questionary.confirm(
        "Do you want to add health checks (liveness/readiness probes)?",
        default=True
    ).ask_async()
    
    need_resources = await questionary.confirm(
        "Do you want to set resource limits (CPU/memory)?",
        default=False
    ).ask_async()
    
    resources = None
    if need_resources:
        cpu_request = await questionary.text(
            "CPU request (m):",
            default="100m"
        ).ask_async()
        cpu_limit = await questionary.text(
            "CPU limit (m):",
            default="500m"
        ).ask_async()
        memory_request = await questionary.text(
            "Memory request (Mi):",
            default="128Mi"
        ).ask_async()
        memory_limit = await questionary.text(
            "Memory limit (Mi):",
            default="512Mi"
        ).ask_async()
        
        resources = {
            'requests': {
                'cpu': cpu_request,
                'memory': memory_request
            },
            'limits': {
                'cpu': cpu_limit,
                'memory': memory_limit
            }
        }
    
    need_configmap = await questionary.confirm(
        "Do you want to generate ConfigMap from .env file?",
        default=False
    ).ask_async()
    
    # Generate manifests
    print(f"\nGenerating Kubernetes manifests for '{app_name}'...")
    
    # Create output directory
    output_dir = Path("k8s_manifests") / app_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate and save Deployment
    deployment = generate_deployment_manifest(app_name, replicas, container_port, need_health_checks, resources)
    save_manifest_to_file(deployment, output_dir / "deployment.yaml")
    
    # Generate and save Service (svc.yaml to match your platform)
    service = generate_service_manifest(app_name, container_port)
    save_manifest_to_file(service, output_dir / "svc.yaml")
    
    # Generate and save Ingress if needed
    if need_ingress:
        ingress = generate_ingress_manifest(app_name, ingress_path)
        save_manifest_to_file(ingress, output_dir / "ingress.yaml")
    
    # Generate and save Kustomization
    kustomization = generate_kustomization_manifest(app_name, need_postgres, need_configmap)
    save_manifest_to_file(kustomization, output_dir / "kustomization.yaml")
    
    # Generate .env file if ConfigMap is needed
    if need_configmap:
        generate_env_file(app_name, output_dir)
    
    # Generate PostgreSQL manifests if needed
    if need_postgres:
        postgres_statefulset, postgres_service = generate_postgres_manifests(app_name)
        save_manifest_to_file(postgres_statefulset, output_dir / "postgres-statefulset.yaml")
        save_manifest_to_file(postgres_service, output_dir / "postgres-service.yaml")
        
        # Create combined postgres.yaml file
        postgres_combined = {
            'apiVersion': 'v1',
            'kind': 'List',
            'items': [postgres_statefulset, postgres_service]
        }
        save_manifest_to_file(postgres_combined, output_dir / "postgres.yaml")
    
    # Success message
    success_message = f"{'='*60}\n"
    success_message += f"{' ' * 15}{'\033[92m'}{'\u2725'}{'\033[0m'} {'\033[92m'}Manifests successfully generated!{'\033[0m'}\n"
    success_message += f"{'='*60}\n"
    success_message += f"{'\033[92m'}{'\u2713'}{'\033[0m'} Location: k8s_manifests/{app_name}/\n"
    success_message += f"{'\033[92m'}{'\u2713'}{'\033[0m'} Files created:\n"
    success_message += f"   - deployment.yaml\n"
    success_message += f"   - svc.yaml\n"
    if need_ingress:
        success_message += f"   - ingress.yaml\n"
    if need_postgres:
        success_message += f"   - postgres.yaml\n"
        success_message += f"   - postgres-statefulset.yaml\n"
        success_message += f"   - postgres-service.yaml\n"
    success_message += f"   - kustomization.yaml\n"
    if need_configmap:
        success_message += f"   - {app_name}.env\n"
    success_message += f"{'='*60}\n"
    success_message += f"{'\033[94m'}{'\2139'}{'\033[0m'} To deploy: kubectl apply -k k8s_manifests/{app_name}/\n"
    success_message += f"{'='*60}"
    
    print(success_message)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
