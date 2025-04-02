pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh '''#!/bin/bash
                echo 'In C or Java, we can compile our program in this step'
                echo 'In Python, we can build our package here or skip this step'
                '''
            }
        }
        
        stage('Test Database') {
            steps {
                sh '''#!/bin/bash
                echo 'Running database tests inside Conda environment "db"'

                # Conda path setup
                CONDA_ROOT="/opt/miniconda3"
                ENV_NAME="db"

                # Ensure Conda is in PATH
                export PATH="$CONDA_ROOT/bin:$PATH"
                source "$CONDA_ROOT/etc/profile.d/conda.sh"

                # Activate Conda environment for database tests
                conda activate $ENV_NAME
                conda info --envs  # Verify Conda activation

                # Change directory and run pytest
                cd database
                pytest

                echo 'Database tests completed successfully!'
                '''
            }
        }

        stage('Test Backend') {
            steps {
                sh '''#!/bin/bash
                echo 'Running backend tests inside Conda environment "mlip"'

                # Conda path setup
                CONDA_ROOT="/opt/miniconda3"
                ENV_NAME="mlip"

                # Ensure Conda is in PATH
                export PATH="$CONDA_ROOT/bin:$PATH"
                source "$CONDA_ROOT/etc/profile.d/conda.sh"

                # Activate Conda environment for backend tests
                conda activate $ENV_NAME
                conda info --envs  # Verify Conda activation

                # Change directory and run pytest
                cd backend
                pytest

                echo 'Backend tests completed successfully!'
                '''
            }
        }

        stage('Test Model') {
            steps {
                sh '''#!/bin/bash
                echo 'Running backend tests inside Conda environment "mlip"'

                # Conda path setup
                CONDA_ROOT="/opt/miniconda3"
                ENV_NAME="mlip"

                # Ensure Conda is in PATH
                export PATH="$CONDA_ROOT/bin:$PATH"
                source "$CONDA_ROOT/etc/profile.d/conda.sh"

                # Activate Conda environment for backend tests
                conda activate $ENV_NAME
                conda info --envs  # Verify Conda activation

                # Change directory and run pytest
                cd model
                pytest --cov=model --cov-report=term-missing tests/

                echo 'Model tests completed successfully!'
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo 'In this step, we deploy our project'
                echo 'Depending on the context, we may publish the project artifact or upload pickle files'
            }
        }
    }
}



