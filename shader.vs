#version 330 core

//uniform mat4 mvp;
uniform vec3 aColor;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 model;

in vec4 vertices;
in vec2 aTexCoord;

out vec3 ourColor;
out vec2 TexCoord;

mat4 translate(float x, float y, float z)
{
    return mat4(
        vec4(1.0, 0.0, 0.0, 0.0),
        vec4(0.0, 1.0, 0.0, 0.0),
        vec4(0.0, 0.0, 1.0, 0.0),
        vec4(  x,   y,   z, 1.0)
    );
}

void main()
{
    
    gl_Position = projection
        * view
        * model//translate(worldPosition.x, worldPosition.y, worldPosition.z)
        * vertices;
        
    TexCoord = vec2(aTexCoord.s, aTexCoord.t);
    ourColor = aColor;
}