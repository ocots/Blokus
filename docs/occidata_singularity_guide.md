# Guide d'utilisation d'Occidata avec Singularity

## Vue d'ensemble

Occidata est un cluster de calcul HPC de l'IRIT qui utilise **Singularity** pour l'exécution de frameworks de Machine Learning et Deep Learning. Ce guide explique comment utiliser Singularity pour entraîner des modèles PyTorch sur GPU.

## Pourquoi Singularity ?

Contrairement à une approche traditionnelle avec modules CUDA, Occidata utilise des **conteneurs Singularity** pour :

- ✅ Éviter les conflits de dépendances entre projets
- ✅ Supporter plusieurs versions de CUDA/Python simultanément
- ✅ Garantir la reproductibilité des environnements
- ✅ Simplifier la gestion des dépendances

## Architecture

```
┌─────────────────────────────────────────┐
│  Login Node (occidata-cluster)          │
│  - Pas de GPU                            │
│  - Soumission de jobs SLURM              │
│  - Préparation de l'environnement        │
└─────────────────────────────────────────┘
                    │
                    │ sbatch
                    ▼
┌─────────────────────────────────────────┐
│  Compute Nodes (GPUNodes partition)     │
│  - GTX 1080 Ti, RTX 6000, RTX 8000, L40S│
│  - Exécution dans conteneur Singularity │
│  - Accès aux GPUs via CUDA               │
└─────────────────────────────────────────┘
```

## Conteneurs disponibles

Les images Singularity sont dans `/apps/containerCollections/CUDA12/` :

| Conteneur | OS | CUDA | PyTorch | Taille |
|-----------|-----|------|---------|--------|
| `pytorch2-NGC-24-02.sif` | Ubuntu 22.04 | 12.3.2 | 2.3.0 | 9.8 GB |
| `pytorch-NGC-25-01.sif` | Ubuntu 22.04 | 12.8 | 2.6.0 | 13 GB |

**Recommandation :** Utiliser `pytorch2-NGC-24-02.sif` (stable et testé).

## Configuration SLURM pour GPU

### Paramètres obligatoires

```bash
#SBATCH --partition=GPUNodes          # Partition avec GPUs
#SBATCH --gres=gpu:1080ti:1           # Type et nombre de GPU
#SBATCH --gres-flags=enforce-binding  # OBLIGATOIRE pour GPU
```

### Types de GPU disponibles

- `gpu:1080ti:1` - NVIDIA GeForce GTX 1080 Ti
- `gpu:rtx6000:1` - NVIDIA RTX 6000
- `gpu:rtx8000:1` - NVIDIA RTX 8000
- `gpu:l40s:1` - NVIDIA L40S

**Limite :** Maximum 4 GPUs par utilisateur sur la plateforme.

## Utilisation de base

### 1. Exécution simple

```bash
singularity exec /apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif python mon_script.py
```

### 2. Script SLURM minimal

```bash
#!/bin/bash
#SBATCH --job-name=mon-training
#SBATCH --partition=GPUNodes
#SBATCH --gres=gpu:1080ti:1
#SBATCH --gres-flags=enforce-binding
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=06:00:00

CONTAINER="/apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif"

singularity exec $CONTAINER python mon_script.py
```

### 3. Vérifier l'accès GPU

```bash
singularity exec /apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0)}')
"
```

## Environnements virtuels Python

### Pourquoi utiliser un venv avec Singularity ?

Les conteneurs incluent PyTorch et CUDA, mais **pas** vos packages spécifiques. Utilisez un venv pour installer vos dépendances additionnelles.

### Création du venv (une seule fois)

```bash
# Sur le login node
singularity shell /apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif

# Dans le conteneur
Singularity> virtualenv --system-site-packages /projects/ctb/mon-projet/mon_venv
Singularity> source /projects/ctb/mon-projet/mon_venv/bin/activate
Singularity> pip install gymnasium tensorboard pandas matplotlib
Singularity> exit
```

**Important :** Utilisez `--system-site-packages` pour hériter de PyTorch du conteneur.

### Utilisation du venv dans un job SLURM

```bash
#!/bin/bash
#SBATCH --job-name=training-avec-venv
#SBATCH --partition=GPUNodes
#SBATCH --gres=gpu:1080ti:1
#SBATCH --gres-flags=enforce-binding

CONTAINER="/apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif"
VENV="/projects/ctb/mon-projet/mon_venv"

singularity exec $CONTAINER bash -c "
  source $VENV/bin/activate
  python mon_script.py
"
```

## Bonnes pratiques

### 1. Gestion de l'espace disque

- ❌ **Ne pas** créer de venv dans `$HOME` (quota 25 GB)
- ✅ **Utiliser** `/projects/ctb/` pour les venvs et données
- ✅ **Définir** `TMPDIR` dans `/projects/` pour éviter "No space left"

```bash
export TMPDIR=/projects/ctb/mon-projet/tmp
export TMP=$TMPDIR
export TEMP=$TMPDIR
```

### 2. Optimisation des performances

- Utiliser `--cpus-per-task=4` minimum pour GPU
- Allouer suffisamment de RAM (`--mem=32G` pour GTX 1080 Ti)
- Limiter le temps avec `--time=HH:MM:SS` (max 72h)

### 3. Debugging

**Tester sur un nœud GPU interactif :**

```bash
srun --partition=GPUNodes --gres=gpu:1080ti:1 --gres-flags=enforce-binding --pty bash
```

Puis exécuter vos commandes manuellement pour débugger.

## Exemple complet : Blokus RL Training

### Structure du projet

```
/projects/ctb/blokus-runner/
├── blokus-venv/              # Environnement virtuel persistant
├── _work/Blokus/Blokus/      # Code du projet (géré par GitHub Actions)
└── tmp/                      # Fichiers temporaires
```

### Script SLURM

```bash
#!/bin/bash
#SBATCH --job-name=blokus-rl
#SBATCH --partition=GPUNodes
#SBATCH --gres=gpu:1080ti:1
#SBATCH --gres-flags=enforce-binding
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=06:00:00
#SBATCH --output=training-%j.out
#SBATCH --error=training-%j.err

set -exo pipefail

CONTAINER="/apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif"
VENV_DIR="/projects/ctb/blokus-runner/blokus-venv"
WORKDIR="/projects/ctb/blokus-runner/_work/Blokus/Blokus/blokus-engine"

cd $WORKDIR

echo "GPU Info:"
singularity exec $CONTAINER nvidia-smi

echo "Starting training..."
singularity exec $CONTAINER bash -c "
  source $VENV_DIR/bin/activate
  python -u scripts/train.py \
    --new \
    --name duo_gpu_test \
    --board-size 14 \
    --episodes 1000 \
    --eval-freq 100 \
    --no-video
"
```

### Soumission

```bash
sbatch mon_script_slurm.sh
```

### Monitoring

```bash
# Voir les jobs en cours
squeue -u $USER

# Voir l'output en temps réel
tail -f training-<job_id>.out

# Annuler un job
scancel <job_id>
```

## Dépannage

### Problème : "module: command not found"

**Cause :** Vous essayez de charger des modules CUDA avec `module load`.

**Solution :** Avec Singularity, **ne pas** utiliser `module load cuda`. CUDA est déjà dans le conteneur.

### Problème : "CUDA not available"

**Vérifications :**

1. Vous êtes sur un nœud GPU ? (`squeue -j <job_id>`)
2. Vous avez `--gres-flags=enforce-binding` ?
3. Le conteneur est le bon ? (pytorch2-NGC-24-02.sif)

```bash
# Test rapide
singularity exec /apps/containerCollections/CUDA12/pytorch2-NGC-24-02.sif nvidia-smi
```

### Problème : "No space left on device"

**Solution :** Définir TMPDIR dans `/projects/`

```bash
export TMPDIR=/projects/ctb/mon-projet/tmp
mkdir -p $TMPDIR
```

### Problème : Venv ne trouve pas PyTorch

**Cause :** Venv créé sans `--system-site-packages`

**Solution :** Recréer le venv avec le flag :

```bash
virtualenv --system-site-packages /projects/ctb/mon-projet/mon_venv
```

## Ressources

- [Documentation Singularity](https://sylabs.io/docs/)
- [NVIDIA NGC Containers](https://ngc.nvidia.com/)
- [Guide Occidata complet](https://occidata.irit.fr/) (accès interne IRIT)

## Checklist de démarrage

- [ ] Créer un venv dans `/projects/ctb/` avec `--system-site-packages`
- [ ] Installer les dépendances spécifiques au projet
- [ ] Tester avec un job court (10 min, 10 épisodes)
- [ ] Vérifier que CUDA est disponible dans les logs
- [ ] Lancer le training complet
- [ ] Monitorer l'utilisation GPU avec `nvidia-smi`

## Support

En cas de problème avec Occidata :
- Email : support-occidata@irit.fr
- Documentation interne : https://occidata.irit.fr/
