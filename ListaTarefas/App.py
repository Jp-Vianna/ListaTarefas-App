import flet as ft


class Tarefa(ft.Column):
    def __init__(self, texto_tarefa, remover_tarefa, tarefa_status_mudou, completada):
        super().__init__()
        self.completada = completada
        self.tarefa_status_mudou = tarefa_status_mudou
        self.remover_tarefa = remover_tarefa
        self.tarefa_check = ft.Checkbox(value=completada, label=texto_tarefa,
                                        on_change=self.mudanca_status, expand=True)
        self.edicao_texto = ft.TextField(value=texto_tarefa,
                                         expand=True)

        self.visivel_tarefas = ft.Row(
            visible=True,
            controls=[
                self.tarefa_check,
                ft.TextButton(text="Editar",
                              on_click=self.editar_tarefa),
                ft.IconButton(icon=ft.icons.REMOVE,
                              on_click=self.deletar_tarefa)
            ]
        )

        self.visivel_edicao = ft.Row(
            visible=False,
            controls=[
                self.edicao_texto,
                ft.TextButton(text="Salvar",
                              on_click=self.salvar_tarefa)
            ]
        )
        self.controls = [self.visivel_tarefas, self.visivel_edicao]

    def mudanca_status(self, e):
        self.completada = self.tarefa_check.value
        self.tarefa_status_mudou(self.completada, self.tarefa_check.label)

    def editar_tarefa(self, e):
        self.visivel_tarefas.visible = False
        self.visivel_edicao.visible = True
        self.update()

    def deletar_tarefa(self, e):
        self.remover_tarefa(self)

    def salvar_tarefa(self, e):
        if self.completada:
            substitui_linha_arquivo(self.edicao_texto.value + '1',
                                    self.tarefa_check.label + '1')
        else:
            substitui_linha_arquivo(self.edicao_texto.value + '0',
                                    self.tarefa_check.label + '0')

        self.tarefa_check.label = self.edicao_texto.value
        self.visivel_tarefas.visible = True
        self.visivel_edicao.visible = False
        self.update()


class ListaTarefas(ft.Column):
    def __init__(self):
        super().__init__()
        self.area_input_tarefa = ft.TextField(hint_text="O que vai fazer hoje?", expand=True)
        self.tarefas = ft.Column()
        self.carrega_arquivo()
        self.incompletas = ft.Text("0 tarefas a fazer.")
        self.width = 600

        self.filtro = ft.Tabs(
            selected_index=0,
            on_change=self.filtro_mudou,
            tabs=[ft.Tab(text="Todas"), ft.Tab(text="A fazer"), ft.Tab(text="Finalizadas")],
        )

        self.controls = [
            ft.Row(
                [ft.Text(value="LISTA DE TAREFAS")],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Row(
                controls=[
                    self.area_input_tarefa,
                    ft.FloatingActionButton(
                        icon=ft.icons.ADD, on_click=self.adiciona_nova_tarefa
                    ),
                ],
            ),
            ft.Column(
                spacing=25,
                controls=[
                    self.filtro,
                    self.tarefas,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.incompletas,
                            ft.OutlinedButton(
                                text="Limpar finalizadas", on_click=self.limpar_finalizadas
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def before_update(self):
        status = self.filtro.tabs[self.filtro.selected_index].text
        contador = 0

        for tarefa in self.tarefas.controls:
            tarefa.visible = (
                status == "Todas"
                or (status == "A fazer" and tarefa.completada is False)
                or (status == "Finalizadas" and tarefa.completada)
            )
            if not tarefa.completada:
                contador += 1

        self.incompletas.value = f"{contador} tarefa(s) a fazer."

    def tarefa_status_mudou(self, mudanca, texto_tarefa):
        if mudanca:
            substitui_linha_arquivo(texto_tarefa + '1', texto_tarefa + '0')
        else:
            substitui_linha_arquivo(texto_tarefa + '0', texto_tarefa + '1')

        self.update()

    def filtro_mudou(self, e):
        self.update()

    def limpar_finalizadas(self, e):
        for tarefa in self.tarefas.controls[:]:
            if tarefa.completada:
                self.remover_tarefa(tarefa)

    def adiciona_nova_tarefa(self, e):
        texto_tarefa = self.area_input_tarefa.value

        if texto_tarefa:
            tarefa = Tarefa(texto_tarefa, self.remover_tarefa, self.tarefa_status_mudou, False)
            self.tarefas.controls.append(tarefa)
            salva_no_arquivo(texto_tarefa)
            self.area_input_tarefa.value = ''
            self.update()
        else:
            pass

    def remover_tarefa(self, tarefa):
        self.tarefas.controls.remove(tarefa)
        remove_linha_arquivo(tarefa.tarefa_check.label)
        self.update()

    def readiciona_tarefa(self, texto_tarefa):
        completada = texto_tarefa[-1:]
        texto_tarefa = texto_tarefa[:-1]

        if completada == '1':
            tarefa = Tarefa(texto_tarefa, self.remover_tarefa, self.tarefa_status_mudou, True)
        else:
            tarefa = Tarefa(texto_tarefa, self.remover_tarefa, self.tarefa_status_mudou, False)

        self.tarefas.controls.append(tarefa)

    def carrega_arquivo(self):
        tarefas = arquivo_para_lista()

        if len(tarefas) != 0:
            for texto_tarefa in tarefas:
                self.readiciona_tarefa(texto_tarefa[:-1])


def salva_no_arquivo(texto_tarefa):
    with open("tarefasarmazenadas.txt", 'a') as arquivo:
        arquivo.write(texto_tarefa + '0\n')


def arquivo_para_lista():
    with open("tarefasarmazenadas.txt", 'r') as arquivo:
        return arquivo.readlines()


def remove_linha_arquivo(texto_tarefa):
    linhas = arquivo_para_lista()
    linhas = [linha for linha in linhas if texto_tarefa not in linha]

    with open("tarefasarmazenadas.txt", "w") as arquivo:
        arquivo.writelines(linhas)


def substitui_linha_arquivo(novo_texto, velho_texto):
    linhas = arquivo_para_lista()

    with open("tarefasarmazenadas.txt", 'w') as arquivo:
        for linha in linhas:
            if linha[:-2] == velho_texto[:-1]:
                arquivo.write(novo_texto + "\n")
            else:
                arquivo.write(linha)


def main(pagina: ft.Page):
    # Título do app.
    pagina.title = "Lista de tarefas"
    # Tamanho da página.
    pagina.window_height = 500
    pagina.window_width = 400

    pagina.update()

    # Inicia aplicativo.
    lista_tarefas = ListaTarefas()

    # Mostra interface.
    pagina.add(lista_tarefas)


ft.app(target=main)
