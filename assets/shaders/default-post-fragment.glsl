#version 330 core

layout(location = 0) out vec4 color;

uniform sampler2D[10] u_textures;

in vec2 f_uv;
in float f_tex;


void main() {

    color = texture(u_textures[int(f_tex)], f_uv) * sin(gl_FragCoord.x / 2.0);

    // convert depth buffer to a grayscale image
    float depth = texture(u_textures[1], f_uv).r;
    color = vec4(vec3(depth), 1.0);
}
