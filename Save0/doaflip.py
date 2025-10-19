def flip_worker():
    for i in range(1001):
        do_a_flip()

def main():
    drones = []
    # 生成32个无人机
    for i in range(32):
        drones.append(spawn_drone(flip_worker))
    
    # 等待所有无人机完成
    for drone in drones:
        wait_for(drone)

if __name__ == "__main__":
    main()