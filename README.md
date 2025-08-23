# 🛡️ Blindando Apps con AWS WAF

Proyecto que demuestra la protección de una aplicación web en AWS. Se contrasta un despliegue vulnerable en ECS contra una arquitectura segura que utiliza AWS WAF para detectar y bloquear ataques comunes como la Inyección SQL.

## 🏛️ Arquitectura Implementada

Para la demostración, implementé dos arquitecturas distintas que permiten analizar el impacto de un ataque y la efectividad de las contramedidas.

### 1. Arquitectura Insegura (Exposición Directa)

En el primer escenario, el contenedor se desplegó con una IP pública asignada directamente, quedando completamente expuesto a internet. Esta configuración sirvió para validar la vulnerabilidad de la aplicación en un entorno no protegido.

```
Usuario → Internet → Contenedor ECS (con IP Pública)
```

### 2. Arquitectura Segura (Protegida con WAF y ALB)

En el segundo escenario, el contenedor se desplegó de forma aislada en una subred privada. El acceso se gestionó a través de un Application Load Balancer (ALB), el cual fue protegido con AWS WAF (Web Application Firewall) para filtrar tráfico malicioso.

```
Usuario → Internet → Application Load Balancer (con AWS WAF) → Security Group → Contenedor ECS (en Subred Privada)
```

## 🛠️ Stack Tecnológico

### Aplicación y Contenerización
- **Backend**: Python, Flask
- **Base de Datos**: MySQL
- **Contenerización**: Docker

### Plataforma Cloud (AWS)
- **Computación**: Amazon ECS (Elastic Container Service) con AWS Fargate
- **Registro de Contenedores**: Amazon ECR (Elastic Container Registry)
- **Redes y Entrega de Contenido**: Application Load Balancer (ALB) y VPC (Subredes Públicas y Privadas)
- **Seguridad**: AWS WAF (Web Application Firewall) y Security Groups

## 🚀 Proceso de Despliegue y Securización

### Fase 1: Contenerización y Registro en ECR

El primer paso fue encapsular la aplicación en una imagen de Docker. Una vez construida la imagen localmente (`docker build`), se subió a un repositorio privado en Amazon ECR. Esto asegura un almacenamiento centralizado y seguro de los artefactos de despliegue.

Para la comunicación con la API de AWS, se utilizó la AWS CLI, previamente configurada con `aws configure`.

### Fase 2: Demostración de la Vulnerabilidad

Para probar la existencia de la vulnerabilidad, se lanzó una tarea de ECS en un clúster configurado con Fargate. La clave de este despliegue fue habilitar la asignación de una IP pública a la tarea.

Una vez accesible, se realizó un ataque de inyección SQL exitoso a través del formulario de login usando el payload:

**Password**: `' OR '1'='1`

Esto concedió acceso no autorizado, confirmando la vulnerabilidad del sistema.

![Ataque SQL Exitoso](https://github.com/bryramirezp/blindando-apps-con-aws-waf/blob/main/ataque-sql-exitoso.png)

### Fase 3: Implementación de la Arquitectura Segura

Para mitigar el riesgo, se desplegó la segunda arquitectura siguiendo un enfoque de defensa en profundidad:

- **Aislamiento de Red**: El servicio de ECS se desplegó en subredes privadas, eliminando cualquier ruta de acceso directo desde internet. La asignación de IP pública fue deshabilitada.

- **Punto de Entrada Controlado**: Se configuró un Application Load Balancer (ALB) como el único punto de entrada. El ALB reside en subredes públicas y su función es redirigir el tráfico de forma segura hacia las tareas de ECS.

- **Firewall de Aplicaciones Web**: Se asoció una Web ACL de AWS WAF directamente al ALB. Para esta ACL, se activó el conjunto de reglas administradas por AWS `AWSManagedRulesSQLiRuleSet`, diseñado específicamente para detectar y bloquear patrones de inyección SQL.

- **Microsegmentación con Security Groups**:
  - El Security Group del ALB se configuró para aceptar tráfico HTTP (puerto 80) desde internet (0.0.0.0/0).
  - El Security Group de la tarea de ECS se configuró para aceptar tráfico únicamente desde el Security Group del ALB, bloqueando cualquier otro intento de conexión.

Al intentar el mismo ataque de inyección SQL contra el endpoint del ALB, la solicitud fue interceptada y bloqueada por AWS WAF, devolviendo un código de estado **403 Forbidden** y demostrando la efectividad de la capa de seguridad implementada.

![Ataque Bloqueado por WAF](https://github.com/bryramirezp/blindando-apps-con-aws-waf/blob/main/ataque-bloqueado-por-waf.png)

## 📂 Estructura del Proyecto

```
/
├── app.py              # Lógica del servidor Flask con la vulnerabilidad
├── app.sql             # Script para configurar la base de datos (referencia)
├── Dockerfile          # Blueprint para la imagen de Docker
├── readme.md           # Este archivo
└── requirements.txt    # Dependencias de Python
```
