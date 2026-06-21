import numpy as np
from numba import njit

@njit
def row_norms(A):
    n = A.shape[0]
    out = np.empty(n)
    for i in range(n):
        out[i] = np.sqrt(A[i,0]*A[i,0] + A[i,1]*A[i,1])
    return out

@njit
def run_simulation(N, D, e, alpha):  
    L = 70.0
    r = 2.0
    r_d = 12.0
    K_atr = 10
    k_atr = 4
    k_alg = 1
    vs = 1
    v_dog = 1.5

    steps = 1000
    runs = 40
    slit = L / 4.0
    points = int(L * 10)

    h = 0.5        # Inertia
    rho_a = 2      # Sheep-sheep repulsion
    rho_d = 1      # Sheep-dog repulsion
    c = 1.5        # Attraction
    alg_str = 1.3  # Alignment

    eps = np.finfo(np.float64).eps
    f_n = r * (N**(2/3))
    pd = r * np.sqrt(N)
    pc = r

    #centre = np.array([L / 2, L / 2])
    goal = np.array([L, L / 2])
    escaped = np.zeros(N)
    N_escaped = np.ones(steps) * N
    N_escaped[0] = 0

    centre = np.random.uniform(4*r, L-4*r, size=2)

    theta_pos = 2*np.pi*np.random.rand(N)
    radius = 3*r*np.sqrt(np.random.rand(N))

    position = centre + np.column_stack((radius*np.cos(theta_pos), radius*np.sin(theta_pos)))

    pos_d = np.random.uniform(r, L - r, (D,2))

    theta_s = 2 * np.pi * np.random.rand(N, 1)
    theta_d = 2 * np.pi * np.random.rand(D, 1)

    velocity = np.empty((N, 2))
    velocity[:,0] = np.cos(theta_s[:,0])
    velocity[:,1] = np.sin(theta_s[:,0])
    
    vel_d = np.empty((D,2))
    vel_d[:,0] = np.cos(theta_d[:,0])
    vel_d[:,1] = np.sin(theta_d[:,0])

    spd_s = np.ones((N, 1)) * vs

    pos_s_dat = np.full((steps, N, 2), np.nan)
    vel_s_dat = np.full((steps, N, 2), np.nan)

    pos_d_dat = np.full((steps, D, 2), np.nan)

    vel_d_dat = np.full((steps, D, 2), np.nan)

    spd_d_dat = np.full((steps, D, 1), np.nan)

    collect_t = np.full((steps, D, 1), np.nan)
    drive_t = np.full((steps, D, 1), np.nan)
    force_slow_t = np.full((steps, D, 1), np.nan)

    pos_s_dat[0, :, :] = position
    vel_s_dat[0, :, :] = velocity
    pos_d_dat[0, :, :] = pos_d
    vel_d_dat[0, :, :] = vel_d
    spd_d_dat[0, :] = v_dog

    # Position and orientation at time t-1
    pos_s_t_1 = np.copy(position)
    pos_d_t_1 = np.copy(pos_d)
    vel_s_t_1 = np.copy(velocity)
    vel_d_t_1 = np.copy(vel_d)

    line_1 = np.zeros(points)
    line_2 = np.linspace(0, L, points)
    line_3 = np.ones(points)
    line_4 = np.linspace(0, L / 2 - slit / 2, points)
    line_5 = np.linspace(L / 2 + slit / 2, L, points)

    wall_1 = np.column_stack((line_1,line_2))
    wall_2 = np.column_stack((line_2,line_1))
    wall_3 = np.column_stack((line_3*L,line_4))
    wall_4 = np.column_stack((line_2,line_3*L))
    wall_5 = np.column_stack((line_3*L,line_2))
    wall_6 = np.column_stack((line_3 * L, line_5))

    boundary = np.vstack((wall_1,wall_2,wall_3,wall_4, wall_6))
    boundary_b = np.vstack((wall_1,wall_2,wall_5,wall_4))

    for t in range(1, steps):
        for i in range(N):
            
            r_all = pos_d_t_1 - pos_s_t_1[i, :]          
            dist_all = row_norms(r_all)                 

            j = np.argmin(dist_all)                      
            r_shp_dg = r_all[j]
            dist_rsd = dist_all[j]

            r_shp_dg = r_shp_dg / (dist_rsd + eps)
            
            # if the sheep beyond interaction radius with dog
            if dist_rsd > r_d:
                r_ij = pos_s_t_1 - pos_s_t_1[i, :]
                r_shp_wall = boundary - pos_s_t_1[i, :]
                
                mag_rsw = row_norms(r_shp_wall)
                mag_rij = row_norms(r_ij)

                rep_j = np.where(mag_rij < r)[0]
                rep_w = np.where(mag_rsw < r)[0]

                if len(rep_j) > 1 or len(rep_w) > 0:
                    rep_j = rep_j[rep_j != i]
                    
                    r_ij_rep = r_ij[rep_j, :] / mag_rij[rep_j][:, np.newaxis]
                    rsw_rep = r_shp_wall[rep_w, :] / mag_rsw[rep_w][:, np.newaxis]
                    
                    r_ij_rep = np.sum(r_ij_rep, axis=0)
                    rsw_rep = np.sum(rsw_rep, axis=0)

                    r_rep = r_ij_rep + rsw_rep
                
                    r_rep = r_rep / (np.linalg.norm(r_rep) + eps)
                    r_rep = -r_rep
                    
                    theta_error = 2 * np.pi * np.random.rand()
                    r_err = np.array([np.cos(theta_error), np.sin(theta_error)])

                    vel_next = h * vel_s_t_1[i, :] + rho_a * r_rep + e * r_err
                    vel_next = vel_next / (np.linalg.norm(vel_next) + eps)

                    position[i, :] = position[i, :] + vs * vel_next
                    vel_s_dat[t, i, :] = vel_next

                    
                else:
                    theta_error = 2 * np.pi * np.random.rand()
                    r_err = np.array([np.cos(theta_error), np.sin(theta_error)])

                    vel_next = e * r_err

                    position[i, :] = position[i, :] + vs * vel_next
                    vel_s_dat[t, i, :] = vel_next
                    

            else: # when dog is seen by the sheep
                r_ij = pos_s_t_1 - pos_s_t_1[i, :]
                r_shp_wall = boundary - pos_s_t_1[i, :]

                mag_rij = row_norms(r_ij)
                mag_rsw = row_norms(r_shp_wall)

                rep_j = np.where(mag_rij < r)[0]
                rep_w = np.where(mag_rsw < r)[0]

                is_err = 0
                
                if len(rep_j) > 1 or len(rep_w) > 0:
                    rep_j = rep_j[rep_j != i]

                    r_ij_rep = r_ij[rep_j, :] / mag_rij[rep_j][:, np.newaxis]
                    rsw_rep = r_shp_wall[rep_w, :] / mag_rsw[rep_w][:, np.newaxis]

                    r_ij_rep = np.sum(r_ij_rep, axis=0)
                    rsw_rep = np.sum(rsw_rep, axis=0)

                    r_rep = r_ij_rep + rsw_rep
                    r_rep = r_rep / (np.linalg.norm(r_rep) + eps)
                    r_rep = -r_rep
                    is_err = 1

                # repulsion from dog
                r_shp_dg = -r_shp_dg

                # attraction towards LCM
                lcm_indices = np.argsort(mag_rij)
                lcm_j = lcm_indices[1 : K_atr + 1] 
                
                perm = np.random.permutation(K_atr)
                lcm_j = lcm_j[perm[:k_atr]]
                
                r_atr = r_ij[lcm_j, :] / (mag_rij[lcm_j][:, np.newaxis] + eps)
                r_atr = np.sum(r_atr, axis=0)
                r_atr = r_atr / (np.linalg.norm(r_atr) + eps)

                # alignment
                perm = np.random.permutation(len(lcm_j))
                l_alg = lcm_j[perm[:k_alg]]
                r_alg = vel_s_t_1[l_alg, :]
                r_alg = np.sum(r_alg, axis=0)
                r_alg = r_alg / (np.linalg.norm(r_alg) + eps)

                # error in copying
                theta_error = 2 * np.pi * np.random.rand()
                r_err = np.array([np.cos(theta_error), np.sin(theta_error)])

                # resultant velocity
                if is_err == 1:
                    vel_next = (h * vel_s_t_1[i, :] + rho_a * r_rep + 
                                rho_d * r_shp_dg + c * r_atr + e * r_err + alg_str * r_alg)
                else:
                    vel_next = (h * vel_s_t_1[i, :] + rho_d * r_shp_dg + 
                                c * r_atr + e * r_err + alg_str * r_alg)

                vel_next = vel_next / (np.linalg.norm(vel_next) + eps)
                position[i, :] = position[i, :] + vs * vel_next
                vel_s_dat[t, i, :] = vel_next
                spd_s[i] = vs

        for i in range(N):
            if (
            escaped[i] == 0
            and position[i, 0] > (L + 1.0)
            and (L - slit) / 2.0 <= position[i, 1] <= (L + slit) / 2.0
            ):
                escaped[i] = 1
        N_escaped[t] = np.sum(escaped)
        if sum(escaped) == N:
            break

        active_idx = np.where(escaped == 0)[0]

        if len(active_idx) == 0:
            # all sheep escaped
            pos_s_dat[t, :, :] = position
            pos_d_dat[t, :] = pos_d
            continue

        # Dynamics of dog
        for d in range(D):
            r_dg_shp = pos_s_t_1 - pos_d_t_1[d]
            dist_rds = row_norms(r_dg_shp)

            r_dg_wall = pos_d_t_1[d] - boundary_b
            dist_dg_wall = row_norms(r_dg_wall)
            idx = np.where(dist_dg_wall < r)[0]

            rwd_rep = r_dg_wall[idx, :] / dist_dg_wall[idx][:, np.newaxis]
            rwd_rep = np.sum(rwd_rep, axis=0)
            rwd_rep = rwd_rep / (np.linalg.norm(rwd_rep) + eps)

            if np.min(dist_rds) <= r:
                vel_next = vel_d_t_1[d] + 5 * rho_a * rwd_rep 
                vel_next = vel_next / (np.linalg.norm(vel_next) + eps)
                pos_d[d] = pos_d[d] + 0.05 * vel_next

                vel_d_dat[t, d, :] = vel_next
                spd_d_dat[t, d] = 0.05
                force_slow_t[t, d] = 1
            
            else:
                grp_centre = np.zeros(2)

                for idx in active_idx:
                    grp_centre[0] += pos_s_t_1[idx,0]
                    grp_centre[1] += pos_s_t_1[idx,1]

                grp_centre /= len(active_idx)

                active_pos = pos_s_t_1[active_idx]
                r_gcm_i = active_pos - grp_centre
                dist_gcm_i = row_norms(r_gcm_i)

                if np.max(dist_gcm_i) >= f_n:
                    # if group is not cohesive
                    max_val = np.max(dist_gcm_i)
                    s_local = np.argmax(dist_gcm_i)
                    s_p = active_idx[s_local]
                    d_behind = dist_gcm_i[s_p] + pc
                    rc = d_behind * (r_gcm_i[s_p, :] / dist_gcm_i[s_p])
                    rc = grp_centre + rc
                    rdc = rc - pos_d_t_1[d]
                    rdc = rdc / ( np.linalg.norm(rdc) + eps)

                    theta_error = 2 * np.pi * np.random.rand()
                    r_err = np.array([np.cos(theta_error), np.sin(theta_error)])

                    vel_next = rdc + e * r_err + 5 * rho_a * rwd_rep
                    vel_next = vel_next / (np.linalg.norm(vel_next) + eps)

                    pos_d[d] = pos_d[d] + v_dog * vel_next 
                    collect_t[t] = 1
                
                else:
                    # if group is cohesive
                    vec_goal_to_gc = grp_centre - goal
                    dist_goal_gc = np.linalg.norm(vec_goal_to_gc)

                    vec_goal_to_gc /= (dist_goal_gc + eps)
                    r_drive = grp_centre + pd * vec_goal_to_gc
                                            
                    r_drive_orient = r_drive - pos_d_t_1[d]
                    r_drive_orient = r_drive_orient / (np.linalg.norm(r_drive_orient) + eps)

                    theta_error = 2 * np.pi * np.random.rand()
                    r_err = np.array([np.cos(theta_error), np.sin(theta_error)])

                    vel_next = r_drive_orient + e * r_err + 5 * rho_a * rwd_rep
                    vel_next = vel_next / (np.linalg.norm(vel_next) + eps)

                    pos_d[d] = pos_d[d] + v_dog * vel_next
                    drive_t[t] = 1 

                vel_d_t_1[d] = vel_next
                vel_d_dat[t, d, :] = vel_next
                spd_d_dat[t, d] = v_dog

        pos_s_dat[t, :, :] = position
        pos_s_t_1 = np.copy(position)
        vel_s_t_1 = vel_s_dat[t, :, :]

        pos_d_dat[t, :] = pos_d
        pos_d_t_1 = np.copy(pos_d)

    return pos_s_dat,vel_s_dat,pos_d_dat, vel_d_dat, spd_d_dat, collect_t, drive_t, force_slow_t, N_escaped