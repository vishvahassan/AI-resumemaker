fragment_shader_source = """
#version 330 core

out vec4 FragColor;
uniform vec2 u_resolution;
uniform float u_power;
uniform float u_time;      // Added for color animation
uniform mat4 u_view_inv;

#define MAX_STEPS 100
#define MAX_DIST 20.0
#define SURF_DIST 0.001

float map(vec3 p) {
    vec3 z = p;
    float dr = 1.0;
    float r = 0.0;
    for (int i = 0; i < 8 ; i++) {
        r = length(z);
        if (r > 2.0) break;
        float theta = acos(z.z / r);
        float phi = atan(z.y, z.x);
        dr = pow(r, u_power - 1.0) * u_power * dr + 1.0;
        float zr = pow(r, u_power);
        theta = theta * u_power;
        phi = phi * u_power;
        z = zr * vec3(sin(theta)*cos(phi), sin(phi)*sin(theta), cos(theta));
        z += p;
    }
    return 0.5 * log(r) * r / dr;
}

vec3 getNormal(vec3 p) {
    vec2 e = vec2(0.001, 0);
    return normalize(map(p) - vec3(map(p-e.xyy), map(p-e.yxy), map(p-e.yyx)));
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    vec3 ro = (u_view_inv * vec4(0, 0, 0, 1)).xyz;
    vec3 rd = normalize((u_view_inv * vec4(uv, -1, 0)).xyz);

    float dO = 0.0;
    int steps = 0;
    for(int i=0; i<MAX_STEPS; i++) {
        vec3 p = ro + rd * dO;
        float dS = map(p);
        if(dS < SURF_DIST || dO > MAX_DIST) break;
        dO += dS;
        steps = i;
    }

    // Background changes color slightly over time
    vec3 color = vec3(0.05, 0.05, 0.1 + 0.05 * sin(u_time * 0.5));
    
    if(dO < MAX_DIST) {
        vec3 p = ro + rd * dO;
        vec3 n = getNormal(p);
        vec3 lightPos = vec3(5.0 * sin(u_time), 5.0, 5.0 * cos(u_time));
        vec3 l = normalize(lightPos - p);
        float diff = max(dot(n, l), 0.0);
        
        // Rainbow cycle logic: using u_time to shift the hue
        vec3 baseCol = 0.5 + 0.5 * cos(u_time + vec3(0, 2, 4) + dO * 0.5);
        
        float iter_glow = float(steps) / float(MAX_STEPS);
        color = baseCol * (diff + 0.2) + (iter_glow * 0.4);
    }
    FragColor = vec4(color, 1.0);
}
"""