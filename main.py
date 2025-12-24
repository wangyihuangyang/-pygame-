# import pygame
#
# pygame.init()
# screen = pygame.display.set_mode((1280,720))
# clock = pygame.time.Clock()
# running = True
# dt = 0
#
# player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
#
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#     screen.fill("purple")
#     pygame.draw.circle(screen,"red",player_pos,40)
#     keys = pygame.key.get_pressed()
#     if keys[pygame.K_w]:
#         player_pos.y -= 300 * dt
#     if keys[pygame.K_s]:
#         player_pos.y += 300 * dt
#     if keys[pygame.K_a]:
#         player_pos.x -= 300 * dt
#     if keys[pygame.K_d]:
#         player_pos.x += 300 * dt
#
#     pygame.display.flip()
#     dt = clock.tick(60)/1000
# pygame.quit()

# import sys,pygame
#
# pygame.init()
#
# size = width,height = 1024,768
# speed = [2,2]
# black = (0,0,0)
# screen = pygame.display.set_mode(size)
# clock = pygame.time.Clock()
# running = True
# xjp = pygame.image.load('Screenshot 2025-12-16 102842.png')
# xjp = pygame.transform.scale(xjp,(width/3,height/3))
# xjprect = xjp.get_rect()
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#     xjprect = xjprect.move(speed)
#     if xjprect.left < 0 or xjprect.right > width:
#         speed[0] = -2*speed[0]
#     if xjprect.top < 0 or xjprect.bottom > height:
#         speed[1] = -2*speed[1]
#     screen.fill(black)
#     screen.blit(xjp, xjprect)
#     pygame.display.flip()
#     clock.tick(60)
# pygame.quit()

import sys,pygame
import time
import random

class Game:
    def __init__(self):
        pygame.init()

        # 窗口创建,game实例的资源
        self.size = self.length,self.width =1024,768
        self.black = (0,0,0)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)

        # 显式状态（Game Flow State）
        self.running = True
        self.game_start = False
        self.game_over = False
        self.game_paused = False

        # 玩家状态
        self.player = Player()

        # 障碍状态
        self.obstacle = ObstacleManager(self.length,self.width)

        # time state
        self.start_time = None

        self.last_penalty_time = 0
        self.penalty_cooldown = 0.3
        self.idle_cooldown = 0.5
        self.survive_time = 0
        self.pause_start_time = None
        self.total_pause_time = 0.0
        self.final_survive_time = 0.0
        self.current_time = time.time()

    # run调度器，安排各类顺序
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(120)

    def handle_events(self):
        # 这是“程序生命周期事件”，不是“游戏规则事件”,和update分离
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # 更新currenttime
        # current_time = time.time()
        hit_obstacle = False
        self.current_time = time.time()
        keys = pygame.key.get_pressed()
        # 空格键启动
        if keys[pygame.K_SPACE] and not self.game_start and not self.game_over:
            self.game_start = True
            self.game_paused = False
            self.start_time = time.time()
            self.player.last_move_time = time.time()
        # 按r重来
        if keys[pygame.K_r] and self.game_over:
            self.game_over = False
            self.game_paused = False
            self.game_start = False
            self.player.lives = 3
            self.player.speed = 2.0
            self.player.rect_x, self.player.rect_y = 200, 170
            self.obstacle.reset()
            self.obstacle.last_obstacle_time = time.time()

        # 加入暂停键
        if keys[pygame.K_p] and self.game_start and not self.game_over:
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.pause_start_time = time.time()
            else:
                self.total_pause_time += time.time() - self.pause_start_time
                self.pause_start_time = None
            pygame.time.delay(200)
    # 逻辑
    # 暂停逻辑
        if self.game_paused:
            return
        # 移动
        moved = False
        if self.game_start:
            moved = self.player.move(keys)
        if moved:
            self.player.last_move_time = time.time()
            # 打墙扣命
        hitwall = False
        if self.player.rect_x < 0:
            self.player.rect_x = 0
            hitwall = True
        if self.player.rect_x + self.player.rect_size > self.length:
            self.player.rect_x = self.length - self.player.rect_size
            hitwall = True
        if self.player.rect_y < 0:
            self.player.rect_y = 0
            hitwall = True
        if self.player.rect_y + self.player.rect_size > self.width:
            self.player.rect_y = self.width - self.player.rect_size
            hitwall = True
        #打墙扣命结算
        if self.game_start and hitwall and self.current_time - self.last_penalty_time > self.penalty_cooldown:
            self.player.take_damage()
            self.last_penalty_time = self.current_time
            pygame.time.delay(300)
        # 障碍逻辑
        if self.game_start:
            obstacle,hit_obstacle = self.obstacle.update(
                self.current_time,self.player.get_rect()
            )
        if hit_obstacle:
            self.player.take_damage()
            self.player.last_move_time = time.time()
            pygame.time.delay(300)
        # 停住扣命

        if self.game_start:

            if not moved and time.time() - self.player.last_move_time >= self.idle_cooldown:
                self.player.take_damage()
                self.player.last_move_time = self.current_time
        # if game_start and not moved and current_time - last_penalty_time > penalty_cooldown:
        #     lives -= 1
        #     last_penalty_time = current_time
        # 生成障碍


        # 加速
        # 先定义survive_time
        if self.game_start:
            self.survive_time = time.time() - self.start_time - self.total_pause_time
        elif self.game_over:
            self.survive_time = self.final_survive_time
        else:
            self.survive_time = 0

        if self.survive_time < 15:
            self.player.speed += self.player.speed_growth
        elif self.survive_time < 25:
            self.player.speed += self.player.after_speed_growth
        # 没有生命时的结算
        if self.player.lives <= 0 and not self.game_over:
            self.final_survive_time = time.time() - self.start_time - self.total_pause_time
            self.game_over = True
            self.game_start = False
            self.game_paused = False
# 看
    def render(self):
        self.screen.fill(self.black)
        # 界面生命剩余和时间渲染
        info_surface = self.font.render(
            f"Lives:{self.player.lives},Time:{self.survive_time:.1f}s",
            True,
            (200,200,200)
        )
        self.screen.blit(info_surface, (10, 10))
        # 角色渲染
        pygame.draw.rect(self.screen, (200,200,200), (self.player.rect_x, self.player.rect_y,self.player.rect_size, self.player.rect_size))
        # 障碍渲染
        for obs in self.obstacle.obstacles:
            pygame.draw.rect(self.screen,(180,50,50),obs)
        # 死亡渲染
        if self.game_over:
            over_text = self.font.render("Game Over", True, (200,50,50))
            retry_text = self.font.render("Press R to Restart", True, (200,200,200))
            time_text = self.font.render(
                f"Time Survived:{self.final_survive_time:.1f}", True, (200,200,200)
            )
            self.screen.blit(over_text, (self.length//2 - 80,self.width//2 - 40))
            self.screen.blit(retry_text, (self.length//2 - 140,self.width//2))
            self.screen.blit(time_text, (self.length // 2 - 140, self.width // 2 - 20))

        pygame.display.flip()
class Player:
    def __init__(self):
        # player state
        self.rect_x = 200
        self.rect_y = 170
        self.rect_size = 30
        self.speed = 2.0
        self.speed_growth = 0.001
        self.after_speed_growth = 0
        self.lives = 3
        self.last_move_time = None
    def move(self,keys):
        moved = False
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if dx != 0 or dy != 0:
            self.rect_x += dx * self.speed
            self.rect_y += dy * self.speed
            moved = True
        return moved
    def take_damage(self):
        self.lives -= 1
    def get_rect(self):
        return pygame.Rect(self.rect_x, self.rect_y, self.rect_size, self.rect_size)

class ObstacleManager:
    def __init__(self,area_width,area_height):
        self.area_width = area_width
        self.area_height = area_height
        self.obstacles = []
        self.obstacle_size = 30
        self.obstacles_interval = 1.0
        self.last_obstacle_time = time.time()
        self.max_obstacle = 25
    def _spawn_obstacle(self, player_rect):
        while True:
            ox = random.randint(0, self.area_width - self.obstacle_size)
            oy = random.randint(0,self.area_height - self.obstacle_size)
            rect = pygame.Rect(ox, oy, self.obstacle_size, self.obstacle_size)
            if not rect.colliderect(player_rect):
                self.obstacles.append(rect)
                if len(self.obstacles) >= self.max_obstacle:
                    self.obstacles.pop(0)
                break
    def update(self,current_time,player_rect):
        collided = False
        # 是否生成障碍
        if current_time - self.last_obstacle_time > self.obstacles_interval:
            self._spawn_obstacle(player_rect)
            self.last_obstacle_time = time.time()
        # 检测是否碰到障碍
        for obs in self.obstacles:
            if obs.colliderect(player_rect):
                collided = True
                break
        return self.obstacles,collided
    def reset(self):
        self.obstacles.clear()
if __name__ == "__main__":
    game = Game()
    game.run()