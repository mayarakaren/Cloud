# Tutorial: Usar um acionador do Amazon S3 para invocar uma função do Lambda para subir arquivos locais ao S3

Neste tutorial, você usará o console para criar uma função do Lambda e configurar um acionador para um bucket do Amazon Simple Storage Service (Amazon S3). Toda vez que você adicionar um objeto ao bucket do Amazon S3, sua função será executada para subir arquivos locais ao S3.

## Pré-requisitos

- Cadastre-se em uma Conta da AWS
- Criar um usuário administrador
- Criar um bucket do Amazon S3

## Passo 1: Criar um bucket do Amazon S3

1. Abra o [console do Amazon S3](https://console.aws.amazon.com/s3) e selecione a página **Buckets**.
2. Selecione **Criar bucket**.
3. Em **General configuration** (Configuração geral):
   - Em **Nome do bucket**, insira um nome global exclusivo que atenda às [regras de nomenclatura de buckets](https://docs.aws.amazon.com/pt_br/AmazonS3/latest/userguide/bucketnamingrules.html) do Amazon S3.
   - Em **AWS Region** (Região da AWS), escolha uma região. Mais adiante no tutorial, você deverá criar sua função do Lambda na mesma região.
4. Deixe todas as outras opções com seus valores padrão e escolha **Criar bucket**.

## Passo 2: Carregar um objeto de teste em um bucket

1. Abra a página **Buckets** do console do Amazon S3 e escolha o bucket que você criou durante a etapa anterior.
2. Escolha **Carregar**.
3. Escolha **Adicionar arquivos** e selecione o objeto que deseja carregar.
4. Selecione **Abrir** e **Carregar**.

## Passo 3: Criação de uma política de permissões

Crie uma política de permissões que permita ao Lambda acessar objetos de um bucket do Amazon S3 e gravar no Amazon CloudWatch Logs.

1. Abra a [página Policies](https://console.aws.amazon.com/iam/home#/policies) (Políticas) do console do IAM.
2. Escolha **Create Policy** (Criar política).
3. Escolha a guia **JSON** e cole a política personalizada a seguir no editor JSON:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:PutLogEvents",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::*/*"
            }
        ]
    }
    ```
4. Escolha **Próximo: etiquetas**.
5. Selecione **Next: Review** (Próximo: revisar).
6. No campo **Nome da política**, insira **s3-upload-tutorial**.
7. Escolha **Criar política**.

## Passo 4: Criar uma função de execução

Um **perfil de execução** é um perfil do AWS Identity and Access Management (IAM) que concede a uma função do Lambda permissão para acessar serviços e recursos da AWS. Nesta etapa, crie um perfil de execução usando a política de permissões que criou na etapa anterior.

1. Abra a [página Roles](https://console.aws.amazon.com/iam/home#/roles) (Funções) no console do IAM.
2. Selecione **Criar função**.
3. Para o tipo de entidade confiável, escolha **Serviço da AWS** e, em seguida, para o caso de uso, selecione **Lambda**.
4. Escolha **Próximo**.
5. Na caixa de pesquisa de política, insira **s3-upload-tutorial**.
6. Nos resultados da pesquisa, selecione a política que você criou (s3-upload-tutorial) e, depois, escolha **Next** (Avançar).
7. Em **Role details** (Detalhes do perfil), para **Role name** (Nome do perfil), insira **lambda-s3-upload-role** e, em seguida, escolha **Create role** (Criar perfil).

## Passo 5: Criar a função do Lambda

Crie uma função do Lambda no console usando o runtime do Python 3.12.

1. Abra a [página Funções](https://console.aws.amazon.com/lambda/home#/functions) do console do Lambda.
2. Verifique se você está na mesma **Região da AWS** em que criou o bucket do Amazon S3. Você pode alterar sua região usando a lista suspensa na parte superior da tela.
3. Escolha a opção **Criar função**.
4. Escolha **Criar do zero**.
5. Em **Basic information** (Informações básicas):
   - Em **Nome da função**, insira **s3-upload-tutorial**.
   - Em **Runtime**, selecione **Python 3.12**.
   - Em **Architecture** (Arquitetura), escolha **x86_64**.
6. Na guia **Alterar função de execução padrão**:
   - Expanda a guia e escolha **Usar uma função existente**.
   - Selecione a **lambda-s3-upload-role** que você criou anteriormente.
7. Escolha **Criar função**.

## Passo 6: Implantar o código da função

Este tutorial usa o runtime do Python 3.12. A função do Lambda irá subir arquivos locais ao bucket do S3.

1. No painel **Código-fonte** no console do Lambda, cole o código no arquivo **lambda_function.py**:

    ```python
    import json
    import boto3
    import os

    s3 = boto3.client('s3')

    def lambda_handler(event, context):
        bucket_name = event['bucket_name']
        file_path = event['file_path']
        key = os.path.basename(file_path)

        try:
            s3.upload_file(file_path, bucket_name, key)
            response = {
                'statusCode': 200,
                'body': json.dumps(f'File {file_path} uploaded to bucket {bucket_name} with key {key}')
            }
        except Exception as e:
            response = {
                'statusCode': 500,
                'body': json.dumps(f'Error uploading file: {str(e)}')
            }
        return response
    ```
2. Escolha **Implantar**.

## Passo 7: Criar o acionador do Amazon S3

1. No painel **Visão geral da função**, escolha **Adicionar gatilho**.
2. Selecione **S3**.
3. Em **Bucket**, selecione o bucket que você criou anteriormente no tutorial.
4. Em **Tipos de eventos**, garanta que a opção **Todos os eventos de criação de objetos** esteja selecionada.
5. Em **Invocação recursiva**, marque a caixa de seleção para confirmar que não é recomendável usar o mesmo bucket do Amazon S3 para entrada e saída.
6. Escolha **Add**.

## Passo 8: Testar sua função do Lambda com um evento fictício

1. Na página de console do Lambda da sua função, escolha a guia **Testar**.
2. Em **Nome do evento**, insira **MyTestEvent**.
3. Em **Evento JSON**, cole o seguinte evento de teste. Substitua os valores conforme necessário:

    ```json
    {
        "bucket_name": "my-bucket",
        "file_path": "/path/to/your/local/file.txt"
    }
    ```
4. Escolha **Salvar**.
5. Escolha **Testar**.

Se a função for executada com êxito, você verá uma saída semelhante à seguinte na guia **Resultados da execução**:

**Response**

```json
{
    "statusCode": 200,
    "body": "\"File /path/to/your/local/file.txt uploaded to bucket my-bucket with key file.txt\""
}
```

## Passo 9: Testar a função do Lambda com o acionador do Amazon S3

Para testar a função com o gatilho configurado, carregue um objeto para o bucket do Amazon S3 usando o console. Para verificar se a função do Lambda foi executada conforme planejado, use o CloudWatch Logs para visualizar a saída da sua função.

### Para carregar um objeto para o bucket do Amazon S3

1. Abra a página **Buckets** do console do Amazon S3 e escolha o bucket que você criou anteriormente.
2. Escolha **Carregar**.
3. Escolha **Adicionar arquivos** e use o seletor de arquivos para escolher um objeto que você deseje carregar.
4. Selecione **Abrir** e **Carregar**.

### Para verificar a invocação da função usando o CloudWatch Logs

1. Abra o [console do CloudWatch](https://console.aws.amazon.com/cloudwatch).
2. Verifique se você está na mesma **Região da AWS** em que criou a função do Lambda.
3. Escolha **Logs** e depois escolha **Grupos de logs**.
4. Escolha o nome do grupo de logs para sua função (/aws/lambda/s3-upload-tutorial).
5. Em **Fluxos de logs**, escolha o fluxo de logs mais recente.

Se sua função tiver sido invocada corretamente em resposta ao gatilho do Amazon S3, você verá uma saída semelhante à seguinte. O **CONTENT TYPE** que você vê depende do tipo de arquivo que você carregou no

 bucket do Amazon S3.

**Log output**

```plaintext
START RequestId: 07ae6b6c-2ce2-4840-bd4d-05c008be6c55 Version: $LATEST
{
    "bucket_name": "my-bucket",
    "file_path": "/path/to/your/local/file.txt"
}
File /path/to/your/local/file.txt uploaded to bucket my-bucket with key file.txt
END RequestId: 07ae6b6c-2ce2-4840-bd4d-05c008be6c55
REPORT RequestId: 07ae6b6c-2ce2-4840-bd4d-05c008be6c55 Duration: 1000 ms Billed Duration: 1000 ms Memory Size: 128 MB Max Memory Used: 50 MB Init Duration: 1000 ms
```

## Limpeza de recursos

Para evitar custos adicionais na sua conta da AWS, exclua os recursos que você criou como parte deste tutorial.

### Para excluir o bucket do Amazon S3

1. Abra a [página Buckets](https://console.aws.amazon.com/s3) no console do Amazon S3.
2. Selecione o bucket que você criou.
3. Escolha **Excluir**.

### Para excluir a função do Lambda

1. Abra a [página Funções](https://console.aws.amazon.com/lambda) do console do Lambda.
2. Selecione a função que você criou.
3. Escolha **Excluir**.

### Para excluir a função de execução do IAM

1. Abra a [página Roles](https://console.aws.amazon.com/iam/home#/roles) do console do IAM.
2. Selecione a função que você criou.
3. Escolha **Excluir função**.

### Para excluir a política do IAM

1. Abra a [página Policies](https://console.aws.amazon.com/iam/home#/policies) do console do IAM.
2. Selecione a política que você criou.
3. Escolha **Excluir política**.