
clear()
substance = 5 * 2**(num_unlocked(Unlocks.Mazes)- 1)
target = 512000000 #目标Treasure数量
def handle():
    while True:
        if num_items(Items.Gold)>= target:
            return
        elif get_entity_type()== Entities.Treasure:
            use_item(Items.Weird_Substance, substance)
            #重复多次确保此时宝箱不再动
            for i in range(6):
                if get_entity_type()== Entities.Treasure:
                    use_item(Items.Weird_Substance, substance)
                    if i == 5:
                        harvest()
                else:
                    break
if __name__=="__main__":
    set_world_size(5)
    #初始化25个无人机
    for _ in range(5):
        for j in range(5):
            spawn_drone(handle)
            move(East)
        move(North)
    #主飞机处理创建迷宫
    while num_items(Items.Gold)< target:
        if measure()== None:
            plant(Entities.Bush)
            use_item(Items.Weird_Substance, substance)
