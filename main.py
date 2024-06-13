from PIL import Image
import os
import random
import discord
from discord.ext import commands
from discord.ui import Button
import discord
import asyncio
import random
from discord.ext import commands
from discord import app_commands, Interaction, Object
from discord.ui import Button, View
from discord import ButtonStyle

# 개별 게임 생성 클래스.

x_axis = {1: 'a', 2: 'b', 3: 'c'}
y_axis_color = {1: 'danger', 2: 'gray', 3: 'gray', 4: 'blurple'}
tile_emoji = {"B상": 1190317171004420237,
              "B왕": 1190317174607319150,
              "B자": 1190317176817729587,
              "B장": 1190317180978470982,
              "R상": 1190317185772556329,
              "R왕": 1190317189299961986,
              "R자": 1190317191426494505,
              "R장": 1190317194861613228,
              "N": 1190620391526387713,
              "R후": 1191742728694935686,
              "B후": 1191742725310132274}


class Setting_gameworld:
    def __init__(self, red_name, blue_name, red_id, blue_id):
        self.map_data = {1: {'a': 'R장', 'b': 'R왕', 'c': 'R상'},
                         2: {'a': 'N', 'b': 'R자', 'c': 'N'},
                         3: {'a': 'N', 'b': 'B자', 'c': 'N'},
                         4: {'a': 'B상', 'b': 'B왕', 'c': 'B장'}
                         }
        self.round = 1
        if random.randint(1, 2) == 1:
            a = blue_name
            b = blue_id
            blue_id = red_id
            blue_name = red_name
            red_id = b
            red_name = a
        self.RedName = red_name
        self.BlueName = blue_name
        self.Red_id = red_id
        self.Blue_id = blue_id
        self.RedDeck = []
        self.BlueDeck = []
        self.turn = 0  # 블루 0 레드 1
        self.result_image_name = f'{self.Blue_id}I{self.Red_id}.png'
        self.game_quit = 1
        self.Bking_hold = 0
        self.Rking_hold = 0

    def image_maker(self):
        background_image_path = r"image/background.png"  # 배경 이미지 파일 경로로 변경해주세요
        background_image = Image.open(background_image_path).convert("RGBA")

        # 결과 이미지 생성
        result_image = Image.new("RGBA", (900, 1200), "white")
        result_image.paste(background_image, (0, 0), background_image)

        for y in range(4):
            for x in range(3):
                x_spot = ['a', 'b', 'c']
                if self.map_data[y+1][x_spot[x]] != "N":
                    image_path = f'image/{self.map_data[y+1][x_spot[x]].strip()}.png'

                    print(image_path)
                    new_image = Image.open(image_path).resize(
                        (250, 250)).convert("RGBA")
                    result_image.paste(
                        new_image, (25 + x * 300, 25 + y * 300), new_image)

        # result_image = result_image.resize((205, 280))
        result_image.save(self.result_image_name)  # 결과 이미지 저장
        return self.result_image_name
        # result_image.show() # 결과 이미지 표시 (선택사항)

    def remove_gamefile(self):
        os.remove(self.result_image_name)

    def move_poro(self):
        if self.turn == 0:
            moveable = ["2a", "2b", "2c", "3a", "3b", "3c", "4a", "4b", "4c"]
        else:
            moveable = ["1a", "1b", "1c", "2a", "2b", "2c", "3a", "3b", "3c"]
        for i in moveable.copy():
            if self.map_data[int(i[:1])][i[1:]][:1] != 'N':
                moveable.remove(i)
        return moveable

    def drop_poro(self, my_yx, what):
        if self.turn == 0:  # blue
            self.BlueDeck.pop(self.BlueDeck.index(what))
        else:
            self.RedDeck.pop(self.RedDeck.index(what))

        self.map_data[int(my_yx[:1])][my_yx[1:]] = what

    def move_radius(self, yx):  # 3b
        moveable = []
        if self.map_data[int(yx[:1])][yx[1:]] != 'N':
            x_conver = {'a': 1, 'b': 2, 'c': 3}
            y = int(yx[:1])  # 3
            x = int(x_conver[yx[1:]])  # 2
            tile = self.map_data[y][yx[1:]][1:]  # 해당위치에 있는 타일의 이름
            tile_color = self.map_data[y][yx[1:]][:1]  # 해당위치에있는 타일의 R or B

            if tile == '장':
                l = [f'{y}{x-1}', f'{y}{x+1}', f'{y+1}{x}', f'{y-1}{x}']

            if tile == '자':
                if tile_color == 'B':
                    l = [f'{y-1}{x}']
                else:
                    l = [f'{y+1}{x}']

            if tile == '상':
                l = [f'{y-1}{x-1}', f'{y+1}{x+1}',
                     f'{y+1}{x-1}', f'{y-1}{x+1}']

            if tile == '왕':
                l = [f'{y-1}{x-1}', f'{y+1}{x+1}', f'{y+1}{x-1}', f'{y-1}{x+1}',
                     f'{y}{x-1}', f'{y}{x+1}', f'{y+1}{x}', f'{y-1}{x}']

            if tile == '후':
                if tile_color == 'B':
                    l = [f'{y-1}{x-1}', f'{y-1}{x+1}', f'{y}{x-1}',
                         f'{y}{x+1}', f'{y+1}{x}', f'{y-1}{x}']
                else:
                    l = [f'{y+1}{x+1}', f'{y+1}{x-1}', f'{y}{x-1}',
                         f'{y}{x+1}', f'{y+1}{x}', f'{y-1}{x}']

            for i in l:  # 오버맵 지우기
                if int(i[:1]) in [0, 5] or int(i[1:]) in [0, 4]:
                    pass
                else:
                    moveable.append(f'{i[:1]}{x_axis[int(i[1:])]}')

            for i in moveable.copy():  # 아군 죽이기 불가
                # self.self.map_data[int(i[:1])][i[1:]]
                if self.map_data[int(i[:1])][i[1:]][:1] == tile_color:
                    moveable.remove(i)
            return moveable
        else:
            return moveable

    def move_tile(self, target_yx, invaded_yx):
        invaded_tile = self.map_data[int(invaded_yx[:1])][invaded_yx[1:]]
        target_tile = self.map_data[int(target_yx[:1])][target_yx[1:]]

        # 후 = 자
        trans = {'후': '자'}

        if invaded_tile != 'N':
            if self.turn == 0:
                self.BlueDeck.append(
                    f"B{trans.get(invaded_tile[1:], invaded_tile[1:])}")
            else:
                self.RedDeck.append(
                    f"R{trans.get(invaded_tile[1:], invaded_tile[1:])}")

        self.map_data[int(invaded_yx[:1])][invaded_yx[1:]
                                           ] = self.map_data[int(target_yx[:1])][target_yx[1:]]
        if target_tile[1:] == '자':
            if self.turn == 0 and int(invaded_yx[:1]) == 1:
                self.map_data[int(invaded_yx[:1])][invaded_yx[1:]] = "B후"
            elif self.turn == 1 and int(invaded_yx[:1]) == 4:
                self.map_data[int(invaded_yx[:1])][invaded_yx[1:]] = "R후"
        self.map_data[int(target_yx[:1])][target_yx[1:]] = 'N'

        # 게임종료 확인
        if invaded_tile[1:] == '왕':
            self.game_quit = "왕죽임"

    def check_king(self):
        if "B왕" in self.map_data[1].values():
            self.Bking_hold += 1
        else:
            self.Bking_hold = 0

        if "R왕" in self.map_data[4].values():
            self.Rking_hold += 1
        else:
            self.Rking_hold = 0

        if self.Bking_hold == 2 or self.Rking_hold == 2:
            self.game_quit = "왕생존"

# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ


# Bot 기본 정보
intents = discord.Intents.default()
intents.message_content = True


client = commands.Bot(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    print(f'PRA_십이장기 실행 {client.user}')


@client.command(name='이미지', help='십이장기 게임실행 명령어입니다.')
async def send_embed(ctx):
    # 로컬 파일 경로
    file_path = 'image\R왕.png'

    # 파일 업로드
    file = discord.File(file_path, filename=file_path)

    # 파일 업로드 메시지 전송
    uploaded_file = await ctx.send(file=file)

    # 업로드된 파일의 URL을 얻기
    file_url = uploaded_file.attachments[0].url

    # 임베드 생성
    embed1 = discord.Embed(title="로컬 파일 임베드", description="로컬 파일을 임베드에 추가합니다.")
    embed1.set_image(url=file_url)  # 파일의 URL을 이미지로 설정
    await uploaded_file.delete()
    # 메시지 전송
    await ctx.send(embed=embed1)


@client.command(name='십이장기', help='십이장기 게임실행 명령어입니다.')
async def make_twelve_chess(ctx, counter_user='bot', time=90):
    if counter_user != 'bot':
        counter_user_id = int(
            counter_user[2:len(counter_user)-1])  # 요청한 유저의 아이디

        # ㅡ 수락/거절 임베드 생성
        embed = discord.Embed(title="<십이장기> 경기를 수락하시겠습니까?",
                              description=f"<@!{ctx.author.id}> 님이 <@!{counter_user_id}> 님에게 대결 요청을 보냈습니다.\n 아래 버튼을 눌러 응답해주세요", color=0x28cc5a)

        # ㅡ 수락 버튼
        async def button_callback(interaction):
            if interaction.user.id == counter_user_id:
                await interaction.response.send_message(content="수락되었습니다!", ephemeral=False)

                author = await client.fetch_user(counter_user_id)  # 주최자 이름
                counter_user_name = author.name  # 초청자 이름
                locals()[f"{ctx.author.id}{counter_user_id}"] = Setting_gameworld(
                    ctx.author, counter_user_name, ctx.author.id, counter_user_id)
                map_name = locals()[f"{ctx.author.id}{counter_user_id}"]
                # 게임 생성 ㅡ 스레드 만들기

                channel = client.get_channel(ctx.channel.id)
                if channel:
                    thread = await channel.create_thread(
                        name=f'🔵{map_name.BlueName} VS 🔴{map_name.RedName}',
                        auto_archive_duration=1440, type=discord.ChannelType.public_thread)  # 시간

                    thread_link = thread.jump_url  # 생성된 쓰레드의 링크

                    embed = discord.Embed(
                        title=f"경기를 시작합니다 ∥ {thread_link}", description=None, color=0x30d95a)  # 경기 시작 임베드
                    game_creat_msg = await ctx.send(embed=embed)

                await m.delete()  # 수락 버튼 임베드 삭제

                while 1:
                    if map_name.turn == 0:
                        turn_player_name = f'🔵<@!{map_name.Blue_id}>'
                        round_user_name = map_name.BlueName
                        next_user_name = map_name.RedName
                    else:
                        turn_player_name = f'🔴<@!{map_name.Red_id}>'
                        round_user_name = map_name.RedName
                        next_user_name = map_name.BlueName

                    # 임베드 만들기
                    file_path = map_name.image_maker()
                    file = discord.File(file_path, filename=file_path)

                    # 파일 업로드 메시지 전송
                    # uploaded_file_channel = client.get_channel(1191707421165490216)
                    uploaded_file = await client.get_channel(1191707421165490216).send(file=file)

                    # 업로드된 파일의 URL을 얻기
                    file_url = uploaded_file.attachments[0].url

                    embed1 = discord.Embed(
                        title=f'라운드 {map_name.round}', color=0x4be255)

                    deck_emoji = ''

                    for i in map_name.BlueDeck:
                        deck_emoji += f"<:emoji_name:{tile_emoji[i]}>"
                    embed1.add_field(
                        name=f'`🔵` {map_name.BlueName}의 포로', value=deck_emoji, inline=True)

                    deck_emoji = ''

                    for i in map_name.RedDeck:
                        deck_emoji += f"<:emoji_name:{tile_emoji[i]}>"
                    embed1.add_field(
                        name=f'`🔴` {map_name.RedName}의 포로', value=deck_emoji, inline=True)

                    # 임베드 생성
                    embed1.set_image(url=file_url)  # 파일의 URL을 이미지로 설정
                    embed1.set_footer(text=f"제한시간 {time}초")
                    # await uploaded_file.delete()

                    # ,file=discord.File(map_name.image_maker()))
                    m1 = await thread.send(content=f'{turn_player_name}님의 차례입니다', embed=embed1)

                    empty_view = discord.ui.View()
                    thread_msg = await thread.send("버튼 준비중..")
                    await thread_msg.edit(content=None, view=Pick1(map_name, thread_msg))

                    def check(message):
                        # 특정 조건에 맞는 메시지인지 확인
                        return int(message.author.id) == 1183419161507008522 and message.channel == thread and (message.content == '―― 착수 완료! ――' or message.content == '―― 항복 선언! ――')
                    try:
                        # ―― 착수 완료! ――라는 메시지를 기다림 (5초 동안)
                        response = await client.wait_for('message', check=check, timeout=time)
                        # await ctx.send(f'You said: {response.content}')

                    except asyncio.TimeoutError:
                        # await thread.send(f'게임이 유기됨. {round_user_name}님이 승리하셨습니다')
                        map_name.game_quit = "유기"
                        break
                    else:
                        # await m1.delete()
                        # 경기 작동 관련 ...
                        map_name.check_king()
                        if map_name.game_quit != 1:
                            break
                        if map_name.turn == 1:
                            map_name.turn = 0
                        else:
                            map_name.turn = 1
                        map_name.round += 1

                # 경기 종료 ㅡㅡ
                game_end_embed = discord.Embed(
                    title=f"종료된 경기입니다 ∥ {thread_link}", description=None, color=0xd93030)  # 경기 종료용 임베드
                await game_creat_msg.edit(embed=game_end_embed)

                if map_name.game_quit == "항복":
                    why = f"{round_user_name}님이 항복을 선언하여 게임이 종료되었습니다"
                    if map_name.turn == 1:
                        win_player_name = f"🔵{map_name.BlueName}"
                    else:
                        win_player_name = f"🔴{map_name.RedName}"

                if map_name.game_quit == "유기":
                    why = f"{round_user_name}님이 제한시간({time}초) 안에 수를 두지 않아 게임이 종료되었습니다"
                    if map_name.turn == 1:
                        win_player_name = f"🔵{map_name.BlueName}"
                    else:
                        win_player_name = f"🔴{map_name.RedName}"

                if map_name.game_quit == "왕죽임":
                    why = f"{round_user_name}님이 상대왕을 잡아 승리하셨습니다"
                    if map_name.turn == 0:
                        win_player_name = f"🔵{map_name.BlueName}"
                    else:
                        win_player_name = f"🔴{map_name.RedName}"

                if map_name.game_quit == "왕생존":
                    why = f"{round_user_name}님이 상대진영에서 생존하여 승리하셨습니다"
                    if map_name.turn == 1:
                        win_player_name = f"🔵{map_name.BlueName}"
                    else:
                        win_player_name = f"🔴{map_name.RedName}"

                # 종료 사유
                # 자 ㅡ 이걸로 통일 ㅡ 승자는 이번 라운드 유저다?
                # 항복 시 턴이 안 바뀐 채 브레이크 ㅡ> 다음 라운드 승자
                # 왕이 먹었을 시 ㅡ> 이번 라운드 유저가 승자
                # 모든 말이 전멸했을 시 -> 이번 라운드가 승리 why? 이번 라운드 유저가 다 죽였을 테니까.
                # 왕이 한 턴을 버텼다? -> 이번 라운드 유저가 승자
                # 그러면 데스 메시지를 어떻게 전달?? map_name.game_quit 굳 ㅅㅂ
                file_path = map_name.image_maker()
                file = discord.File(file_path, filename=file_path)

                # 파일 업로드 메시지 전송
                # uploaded_file_channel = client.get_channel(1191707421165490216)
                uploaded_file = await client.get_channel(1191707421165490216).send(file=file)

                # 업로드된 파일의 URL을 얻기
                file_url = uploaded_file.attachments[0].url

                game_end_embed = discord.Embed(
                    title=f'게임 종료 🔵{map_name.BlueName} VS 🔴{map_name.RedName}', description=why, color=0xd93030)  # 경기 종료용 임베드
                game_end_embed.add_field(
                    name="라운드", value=f'`{map_name.round}`', inline=True)
                game_end_embed.add_field(
                    name="승자", value=f'`{win_player_name}`', inline=True)
                game_end_embed.set_image(url=file_url)
                await thread.send(embed=game_end_embed)

                await thread.edit(locked=True)
                map_name.remove_gamefile()
            else:
                await interaction.response.send_message(content="죄송합니다. 요청한 유저가 아닙니다.", ephemeral=True)

        async def button_callback2(interaction):
            if interaction.user.id == int(counter_user_id):
                await interaction.response.send_message(content="거절되었습니다.", ephemeral=False)
                await m.delete()
            else:
                await interaction.response.send_message(content="죄송합니다. 요청한 유저가 아닙니다.", ephemeral=True)

        button1 = Button(label='수락', style=discord.ButtonStyle.green)
        button2 = Button(label='거절', style=discord.ButtonStyle.danger)
        button1.callback = button_callback
        button2.callback = button_callback2

        view = View()
        view.add_item(button1)
        view.add_item(button2)
        m = await ctx.send(embed=embed, view=view)
    # elif counter_user_id == ctx.author.id:
    #    await ctx.send('본인과의 승부는 불가능합니다.')
    else:
        await ctx.send('현재 봇과의 매치는 준비되있지 않습니다.')

    await asyncio.sleep(180)
    try:
        await m.delete()
        await ctx.send("3분간 수락되지 않아 경기가 취소되었습니다.")
    except:
        pass
# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
'''
@client.command(name="판")
async def button(ctx):
    view = Pick1(p1,ctx)
    await ctx.reply(file=discord.File(p1.image_maker()),view=view)
'''


class Pick1(discord.ui.View):
    def __init__(self, class_name, thread_msg):
        super().__init__()
        # 버튼 라벨 2차원 리스트
        if class_name.turn == 0:
            deck = class_name.BlueDeck
            round_user_id = class_name.Blue_id
            round_color = "B"
        else:
            deck = class_name.RedDeck
            round_user_id = class_name.Red_id
            round_color = "R"
        button_labels = [['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], [
            'a3', 'b3', 'c3'], ['a4', 'b4', 'c4']]

        # 동적으로 버튼 생성 및 추가
        for row_index, row_labels in enumerate(button_labels, start=1):
            for col_index, label in enumerate(row_labels, start=1):
                # 버튼의 행과 열을 2차원 리스트의 인덱스로 지정
                btn = (discord.ui.Button(label=' '*row_index*col_index, style=discord.ButtonStyle.red,
                                        emoji=f"<:emoji_name:{tile_emoji[class_name.map_data[row_index][x_axis[col_index]]]}> ", row=row_index, custom_id=f"Pi1{row_index}{x_axis[col_index]}"))
                if row_index == 1:
                    btn.style = discord.ButtonStyle.red
                elif row_index == 2 or row_index == 3:
                    btn.style = discord.ButtonStyle.grey
                elif row_index == 4:
                    btn.style = discord.ButtonStyle.blurple

                if class_name.map_data[row_index][x_axis[col_index]][:1] == round_color and len(class_name.move_radius(f"{row_index}{x_axis[col_index]}")) > 0:
                    disable = False
                else:
                    disable = True
                btn.disabled = disable
                self.add_item(btn)

        if len(deck) == 0:
            disable = True
        else:
            disable = False
        poro_btn = discord.ui.Button(
            label='포로', style=discord.ButtonStyle.green, row=1, custom_id=f"Pi1포로")
        poro_btn.disabled = disable

        self.add_item(poro_btn)
        self.add_item(discord.ui.Button(
            label='항복', style=discord.ButtonStyle.green, row=2, custom_id=f"Pi1항복"))

        @client.event
        async def on_interaction(interaction: discord.Interaction):
            btn_data = interaction.data['custom_id']
            if btn_data[:3] == 'Pi1':  # 클래스가 Pick1인지 확인
                btn_data = btn_data[3:]
                if btn_data == '항복' and (interaction.user.id == class_name.Blue_id or interaction.user.id == class_name.Red_id):
                    class_name.game_quit = "항복"
                    await interaction.response.send_message("―― 항복 선언! ――")
                elif btn_data == '포로' and interaction.user.id == round_user_id:
                    await interaction.response.send_message(content=f"착수하실 포로를 선택해주세요", ephemeral=True)
                    await thread_msg.edit(view=Select_Poro(class_name, thread_msg))
                    # await thread_msg.edit(view=Pick3(class_name,thread_msg,btn_data))
                else:
                    if interaction.user.id == round_user_id:
                        # Pick 2로 수 넘기기
                        await thread_msg.edit(view=Pick2(class_name, thread_msg, btn_data, class_name.move_radius(btn_data)))
                        await interaction.response.send_message(content=f"{btn_data} 착수 상태로 변경되었습니다", ephemeral=True)
                        # await interaction.response.send_message("―― 착수 완료! ――")
                        # await interaction.delete_original_message()
                    else:
                        await interaction.response.send_message(content="현재 차례의 유저가 아닙니다.", ephemeral=True)


class Pick2(discord.ui.View):  # 기물 움직이기
    def __init__(self, class_name, thread_msg, my_yx, moveable=[]):
        super().__init__()
        # 버튼 라벨 2차원 리스트
        if class_name.turn == 0:
            deck = class_name.BlueDeck
            round_user_id = class_name.Blue_id
            round_color = "B"
        else:
            deck = class_name.RedDeck
            round_user_id = class_name.Red_id
            round_color = "R"
        button_labels = [['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], [
            'a3', 'b3', 'c3'], ['a4', 'b4', 'c4']]
        # 함수(좌표)
        # 반경 명단 리스트는 녹색으로 표기되도록 설계해야함. + 반경 함수

        # 동적으로 버튼 생성 및 추가
        for row_index, row_labels in enumerate(button_labels, start=1):
            for col_index, label in enumerate(row_labels, start=1):
                # 버튼의 행과 열을 2차원 리스트의 인덱스로 지정

                btn = (discord.ui.Button(label=' '*row_index*col_index, style=discord.ButtonStyle.red,
                       emoji=f"<:emoji_name:{tile_emoji[class_name.map_data[row_index][x_axis[col_index]]]}> ", row=row_index, custom_id=f"Pi2{row_index}{x_axis[col_index]}"))
                if row_index == 1:
                    btn.style = discord.ButtonStyle.red
                elif row_index == 2 or row_index == 3:
                    btn.style = discord.ButtonStyle.grey
                elif row_index == 4:
                    btn.style = discord.ButtonStyle.blurple

                if f"{row_index}{x_axis[col_index]}" in moveable:
                    btn.style = discord.ButtonStyle.green
                    disable = False
                else:
                    disable = True
                btn.disabled = disable
                self.add_item(btn)
        self.add_item(discord.ui.Button(
            label='선택취소', style=discord.ButtonStyle.danger, row=1, custom_id=f"Pi2취소"))

        @client.event
        async def on_interaction(interaction: discord.Interaction):
            btn_data = interaction.data['custom_id']
            if btn_data[:3] == 'Pi2':  # 클래스가 Pick1인지 확인
                btn_data = btn_data[3:]
                if interaction.user.id == round_user_id:
                    if btn_data == '취소':
                        await thread_msg.edit(view=Pick1(class_name, thread_msg))
                        await interaction.response.send_message(content="기본 버튼으로 변경되었습니다", ephemeral=True)
                    else:
                        empty_view = discord.ui.View()
                        # await thread_msg.edit(content='',view=empty_view) #버튼 삭제
                        await thread_msg.delete()
                        class_name.move_tile(my_yx, btn_data)
                        await interaction.response.send_message("―― 착수 완료! ――")
                else:
                    await interaction.response.send_message(content="현재 차례의 유저가 아닙니다.", ephemeral=True)


class Pick3(discord.ui.View):  # 포로
    def __init__(self, class_name, thread_msg, what='N'):
        super().__init__()
        # 버튼 라벨 2차원 리스트
        if class_name.turn == 0:
            deck = class_name.BlueDeck
            round_user_id = class_name.Blue_id
            round_color = "B"
        else:
            deck = class_name.RedDeck
            round_user_id = class_name.Red_id
            round_color = "R"
        button_labels = [['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], [
            'a3', 'b3', 'c3'], ['a4', 'b4', 'c4']]
        # 함수(좌표)
        moveable = class_name.move_poro()
        # 동적으로 버튼 생성 및 추가
        for row_index, row_labels in enumerate(button_labels, start=1):
            for col_index, label in enumerate(row_labels, start=1):
                # 버튼의 행과 열을 2차원 리스트의 인덱스로 지정
                btn = (discord.ui.Button(label=' '*row_index*col_index, style=discord.ButtonStyle.red,
                       emoji=f"<:emoji_name:{tile_emoji[class_name.map_data[row_index][x_axis[col_index]]]}>", row=row_index, custom_id=f"Pi3{row_index}{x_axis[col_index]}"))
                if row_index == 1:
                    btn.style = discord.ButtonStyle.red
                elif row_index == 2 or row_index == 3:
                    btn.style = discord.ButtonStyle.grey
                elif row_index == 4:
                    btn.style = discord.ButtonStyle.blurple

                if f"{row_index}{x_axis[col_index]}" in moveable:
                    btn.style = discord.ButtonStyle.green
                    disable = False
                else:
                    disable = True
                btn.disabled = disable
                self.add_item(btn)
        self.add_item(discord.ui.Button(
            label='선택취소', style=discord.ButtonStyle.danger, row=1, custom_id=f"Pi3취소"))

        @client.event
        async def on_interaction(interaction: discord.Interaction):
            btn_data = interaction.data['custom_id']
            if btn_data[:3] == 'Pi3':  # 클래스가 Pick1인지 확인
                btn_data = btn_data[3:]
                if interaction.user.id == round_user_id:
                    if btn_data == '취소':
                        await thread_msg.edit(view=Pick1(class_name, thread_msg))
                        await interaction.response.send_message(content="기본 버튼으로 변경되었습니다", ephemeral=True)
                    else:
                        class_name.drop_poro(btn_data, what)
                        await thread_msg.delete()
                        await interaction.response.send_message("―― 착수 완료! ――")
                else:
                    await interaction.response.send_message(content="현재 차례의 유저가 아닙니다.", ephemeral=True)


class Select_Poro(discord.ui.View):
    def __init__(self, class_name, thread_msg):
        super().__init__()

        # 버튼 라벨 2차원 리스트
        if class_name.turn == 0:
            deck = class_name.BlueDeck
            round_user_id = class_name.Blue_id
            round_color = "B"
        else:
            deck = class_name.RedDeck
            round_user_id = class_name.Red_id
            round_color = "R"

        deck_list = []
        deck_list.append(discord.SelectOption(
            label="취소", emoji="❌", description="포로 선택을 취소합니다.",))
        for i in range(len(deck)):
            deck_list.append(discord.SelectOption(
                label=f'{deck[i]}{"­"*i}', emoji=f"<:emoji_name:{tile_emoji[deck[i]]}>", description="ㅡ 설명",))
        # Select 사용
        select_menu = discord.ui.Select(
            custom_id="select_poro_menu", options=deck_list, placeholder="카드를 선택해주세요", min_values=1, max_values=1)
        self.add_item(select_menu)

        @client.event
        async def on_interaction(interaction: discord.Interaction):
            if interaction.user.id == round_user_id:
                if interaction.data['values'][0] != "취소":
                    what = interaction.data['values'][0][:2]
                    await thread_msg.edit(view=Pick3(class_name, thread_msg, what))
                    await interaction.response.send_message(content=f"{what}를 선택하셨습니다.", ephemeral=True)
                else:
                    await thread_msg.edit(view=Pick1(class_name, thread_msg))
                    await interaction.response.send_message(content="기본 버튼으로 변경되었습니다", ephemeral=True)
            else:
                await interaction.response.send_message(content="현재 차례의 유저가 아닙니다.", ephemeral=True)


@client.event
async def on_interaction(interaction: discord.Interaction):
    btn_data = interaction.data['custom_id']
    if btn_data[:3] == 'Pi1':  # 클래스가 Pick1인지 확인
        btn_data = btn_data[3:]
        coordinate = f"{x_axis[int(btn_data[0:1])]}{btn_data[1:]}"
        await interaction.response.send_message(coordinate)
# ㅡㅡㅡㅡ'''





client.run('토큰을 넣으세요')
