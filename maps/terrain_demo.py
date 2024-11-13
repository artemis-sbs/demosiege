from sbs_utils import scatter
import random
from sbs_utils.procedural.ship_data import plain_asteroid_keys
from sbs_utils.procedural.spawn import terrain_spawn, npc_spawn
from sbs_utils.procedural.query import to_id, to_object
from sbs_utils.procedural.inventory import set_inventory_value

from sbs_utils.scatter import ring as scatter_ring
from sbs_utils.faces import set_face, random_terran
from sbs_utils.vec import Vec3

import math


def demo_spawn_stations(difficulty, lethal_value, x_min=-32500, x_max=32500, center=None, min_num=0):
    if center is None:
        center = Vec3(0,0,0)
    pos = Vec3(center)
    startZ = -50000
    count = [7,7,6,6,5,5,4,4,3,2,2,2]
    num_stations = count[difficulty]
    station_step = 100000/num_stations

    #print(f"Station Center at: {pos.x} {pos.y} {pos.z}")
    # for each station
    for index in range(num_stations):
        stat_type = "starbase_command"
        pos.x = center.x + random.uniform(x_min, x_max)
        pos.y = center.y + random.random()*2000-1000
        pos.z = center.z + startZ #+ random.random()*station_step/3  -   station_step/6
    #    _spawned_pos.append(pos)
        startZ += station_step

        #make the station ----------------------------------
        #print(f"Station at: {pos.x} {pos.y} {pos.z} - {startZ} {station_step}")
        name = f"DS {index+1}"
        s_roles = f"tsn, station"
        station_object = npc_spawn(*pos, name, s_roles, stat_type, "behav_station")
        ds = to_id(station_object)
        set_face(ds, random_terran(civilian=True))

        # wrap a minefield around the station ----------------------------
        if lethal_value > 0:
            startAngle = random.randrange(0,359)
            angle = random.randrange(90,170)
            angle = 170
            endAngle = startAngle + angle
            
            
            depth = 1   #random.randrange(2,3)
            width = int(5 * lethal_value)
            widthArray = [int(angle / 5.0)]
            inner = random.randrange(1200,1500)
            cluster_spawn_points = scatter_ring(width, depth, pos.x,pos.y,pos.z, inner, inner, startAngle, endAngle)
            
            # Random type, but same for cluster
            for v2 in cluster_spawn_points:
                #keep value between -500 and 500??
                mine_obj = terrain_spawn( v2.x, v2.y + random.randrange(-300,300), v2.z,None, "#,mine", "danger_1a", "behav_mine")
                mine_obj.blob.set("damage_done", 5)
                mine_obj.blob.set("blast_radius", 1000)
                mine_obj.engine_object.blink_state = -5


# make a few random clusters of Asteroids
def demo_asteroid_clusters(terrain_value, center=None):
    if center is None:
        center = Vec3(0,0,0)

    #t_min = terrain_value * 7
    #t_max = t_min * 3
    t_max_pick = [0,8,10, 12,16]
    t_min = t_max_pick[terrain_value]
    t_max = t_min * 2
    spawn_points = scatter.box(random.randint(t_min,t_max), center.x, center.y, center.z, 100000, 1000, 100000, centered=True)

    asteroid_types = ["plain_asteroid_6"]
    for v in spawn_points:
        
        amount = random.randint(t_min,t_max)//2
        size = amount *3
        # the more you have give a bit more space
        ax = random.randint(-20,20)
        ay = random.randint(-150,150)
        az = random.randint(-20,20)
        #cluster_spawn_points = scatter_box(amount, v.x, 0,v.z, amount*50, amount*20,amount*200, centered=True, ax, ay, az )
        cluster_spawn_points = scatter.box(amount,  v.x, 0,v.z, size*150, size*50,size*200, True, 0, ay, 0 )

        scatter_pass = 0
        for v2 in cluster_spawn_points:
            a_type = random.choice(asteroid_types)

            asteroid = terrain_spawn(v2.x, v2.y, v2.z,None, "#,asteroid", a_type, "behav_asteroid")
            asteroid.engine_object.steer_yaw = random.uniform(0.0001, 0.003)
            asteroid.engine_object.steer_pitch = -random.uniform(0.0001, 0.003)
            asteroid.engine_object.steer_roll = random.uniform(0.0001, 0.003)

            # Some big, some small
            # big are more spherical
            # 1 in 4 big
            if scatter_pass%4 != 0:
                sx = random.uniform(7.0, 15.0)
                sy = sx + random.uniform(-1.2, 1.2)
                sz = sx + random.uniform(-1.2, 1.2)
                sm = min(sx, sy)
                sm = min(sm, sz)
                er = asteroid.engine_object.exclusion_radius
                er *= sm/2
                asteroid.engine_object.exclusion_radius = er
            else:
                sx = random.uniform(2.5, 5)
                sy = random.uniform(2.5, 5)
                sz = random.uniform(2.5, 5)
                sm = min(sx, sy)
                sm = min(sm, sz)
            scatter_pass += 1
            #er = asteroid.blob.get("exclusionradius",0)
            #er *= sm

            asteroid.blob.set("local_scale_x_coeff", sx)
            asteroid.blob.set("local_scale_y_coeff", sy)
            asteroid.blob.set("local_scale_z_coeff", sz)
            

            # if scatter_pass==0:
            #     continue
            # # else:
            # #     continue

            # #
            # # Sphere od smaller asteroids
            # #
            this_amount = random.randint(7,12)
            little = scatter.box(this_amount,  v2.x, 0,v2.z, amount*150, amount*50,amount*200, True)
            #little = scatter.sphere(random.randint(2,6), v2.x, v2.y, v2.z, 300, 800)
            # little = scatter.sphere(random.randint(12,26), v2.x, v2.y, v2.z, 800)
            
            for v3 in little: 
                a_type = random.choice(asteroid_types)

                asteroid = terrain_spawn(v3.x, v3.y, v3.z,None, "#,asteroid", a_type, "behav_asteroid")
                asteroid.engine_object.steer_yaw = random.uniform(0.0001, 0.003)
                asteroid.engine_object.steer_pitch = -random.uniform(0.0001, 0.003)
                asteroid.engine_object.steer_roll = random.uniform(0.0001, 0.003)
                sx1 = random.uniform(0.3, 1.0)
                sy1 = random.uniform(0.3, 1.0)
                sz1 = random.uniform(0.3, 1.0)
                sm1 = max(sx, sy)
                sm1 = max(sm, sz)
                er = asteroid.engine_object.exclusion_radius
                er *= sm1
                asteroid.engine_object.exclusion_radius = 0
                

                asteroid.blob.set("local_scale_x_coeff", sx1)
                asteroid.blob.set("local_scale_y_coeff", sy1)
                asteroid.blob.set("local_scale_z_coeff", sz1)


