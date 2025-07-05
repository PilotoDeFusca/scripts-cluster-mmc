# Script responsavel por executar os testes de "corrida" entre a GPU completa e seus MIGs.
# A intenção é executar vários testes para responder a seguinte pergunta: 
# O que é mais rapido? A GPU inteira rodando 100 jobs em sequencia, ou vários MIGs dividindo esses jobs entre si 
# e rodando-os em paralelo?

# Esse script se diferencia do outro porque está usando WAIT ao inves de SLEEP e rodando na 1.0

import os

devices = [ # id dos migs
'MIG-365f9ce1-c091-57a7-8ef3-4cbb45dcca47',
'MIG-40144944-d4a9-585d-978e-1ace55172139',
'MIG-0ebc0c9f-adc4-59a6-af10-200d49046bb5',
'MIG-effedeec-21b5-5ad2-904d-f4d06708ac4d'
]

gpu_id = "GPU-fd7e14c3-91ce-6c4b-e736-393c0d0537ef" # ID da gpu completa

maquina = '1-1' # maquina que vai executar os jobs, pode ser 1-0 ou 1-1
tamanho_mig = '1g-20gb' # perfil do mig

benchmarks = ['bt.C','cg.C','ep.C','ft.C','is.C','lu.C','mg.C','sp.C']

for benchmark in benchmarks: # cria as pastas caso não existam. Essa sequencia ficou meio ruim, mas da pra usar sem problema
    try:
        os.system(f'mkdir /home/pabloh/2025/saidas/compute-{maquina}/{benchmark.replace(".C","")}/{tamanho_mig} -p')
        os.system(f'mkdir /home/pabloh/2025/saidas/compute-{maquina}/{benchmark.replace(".C","")}/gpu -p')
    except:
        pass

for benchmark in benchmarks:
    for index in range(1,101):
        benchmark_no_size = benchmark.replace(".C","")
        roteiro = f'''
#!/bin/bash
#----------------------------------------------------------
# Job name
#PBS -N test

# Name of stdout output file
#PBS -o /home/pabloh/2025/saidas/lixeira/out/
#PBS -e /home/pabloh/2025/saidas/lixeira/err/
# Total number of nodes and MPI tasks/node requested
#PBS -l nodes=compute-{maquina}:ppn=4

# Run time (hh:mm:ss) - 1.5 hours
#PBS -l walltime=01:30:00
#----------------------------------------------------------

# Change to submission directory
cd $PBS_O_WORKDIR

cat $PBS_NODEFILE

# Launch MPI-based executable
time CUDA_VISIBLE_DEVICES={devices[0]} ./mig >> /home/pabloh/2025/saidas/compute-{maquina}/{benchmark_no_size}/{tamanho_mig}/mig-{benchmark_no_size}-{index}-{devices[0]} &
time CUDA_VISIBLE_DEVICES={devices[1]} ./mig >> /home/pabloh/2025/saidas/compute-{maquina}/{benchmark_no_size}/{tamanho_mig}/mig-{benchmark_no_size}-{index}-{devices[1]} &
time CUDA_VISIBLE_DEVICES={devices[2]} ./mig >> /home/pabloh/2025/saidas/compute-{maquina}/{benchmark_no_size}/{tamanho_mig}/mig-{benchmark_no_size}-{index}-{devices[2]} &
time CUDA_VISIBLE_DEVICES={devices[3]} ./mig >> /home/pabloh/2025/saidas/compute-{maquina}/{benchmark_no_size}/{tamanho_mig}/mig-{benchmark_no_size}-{index}-{devices[3]} &


pid=$!
wait $pid

'''
        
        # No script original (me refiro à primeira execução desse script), havia linhas antes de `sleep 60` que executavam, sequencialmente na GPU inteira,
        # o mesmo número de jobs que estão sendo executados em paralelo nos migs (exemplo: 4 migs, 1 job pra cada mig e 4 pra GPU completa)
         
        with open('/home/pabloh/2025/scripts/roteiro', 'w') as roteiro_file: # escreve o roteiro
            roteiro_file.write(roteiro)

        with open('/home/pabloh/2025/scripts/mig', 'w') as mig_script: # escreve o conteúdo do arquivo './mig' que é o que ta sendo executado dentro do roteiro (ver linhas 64 até 67)
            mig_script.write(f'/home/pabloh/NPB-GPU/CUDA/bin/{benchmark}')

        # executa o roteiro
        os.system('qsub /home/pabloh/2025/scripts/roteiro')
