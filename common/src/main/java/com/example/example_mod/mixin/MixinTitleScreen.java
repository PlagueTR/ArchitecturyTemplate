package com.example.example_mod.mixin;

import com.example.example_mod.Main;

import net.minecraft.client.gui.screens.TitleScreen;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(TitleScreen.class)
public abstract class MixinTitleScreen {

    @Unique
    private static boolean example_mod$saidHello;

    @Inject(method = "init()V", at = @At("TAIL"))
    private void example_mod$onInit(CallbackInfo ci) {
        if (!example_mod$saidHello && Main.getConfig().isEnableMod()) {
            Main.LOGGER.info("Hello from MixinTitleScreen");
            example_mod$saidHello = true;
        }
    }

}
